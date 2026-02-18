from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Document, Analysis, PlagiarismMatch, AnalysisLog
from app.services.detection_engine import DetectionEngine
from datetime import datetime
import time
import threading

analysis_bp = Blueprint("analysis", __name__)
engine = DetectionEngine()


# ==========================================================
# BACKGROUND ANALYSIS TASK
# ==========================================================

def run_analysis(app, analysis_id, document_id, user_id):
    """
    Background task for running plagiarism + AI analysis
    """

    with app.app_context():  # CRITICAL FIX for background threads
        try:
            analysis = Analysis.query.get(analysis_id)
            document = Document.query.get(document_id)

            if not analysis or not document:
                return

            analysis.status = "processing"
            db.session.commit()

            start_time = time.time()

            # ===============================
            # Run Detection Engine
            # ===============================
            result = engine.analyze_text(document.extracted_text)

            plagiarism_score = result["plagiarism_score"]
            ai_probability = result["ai_probability"]
            matches = result["plagiarism_matches"]

            # ===============================
            # Save Matches
            # ===============================
            for match in matches:
                db_match = PlagiarismMatch(
                    analysis_id=analysis_id,
                    source_url=match["source_url"],
                    source_title=match["source_url"],
                    matched_text=match["matched_text"],
                    original_text=match["matched_text"],
                    similarity_score=match["similarity_score"],
                    match_type="web_semantic",
                    start_index=0,
                    end_index=len(match["matched_text"])
                )
                db.session.add(db_match)

            # ===============================
            # Update Analysis Record
            # ===============================
            analysis.overall_similarity = plagiarism_score
            analysis.ai_generated_probability = ai_probability
            analysis.status = "completed"
            analysis.completed_at = datetime.utcnow()
            analysis.processing_time = round(
                time.time() - start_time,
                2
            )

            db.session.commit()

            # ===============================
            # Log Completion
            # ===============================
            log = AnalysisLog(
                user_id=user_id,
                analysis_id=analysis_id,
                action="analysis_completed",
                details={
                    "similarity": plagiarism_score,
                    "ai_probability": ai_probability,
                    "match_count": len(matches)
                }
            )

            db.session.add(log)
            db.session.commit()

        except Exception as e:
            print(f"Analysis error: {str(e)}")

            analysis = Analysis.query.get(analysis_id)

            if analysis:
                analysis.status = "failed"
                analysis.error_message = str(e)
                analysis.completed_at = datetime.utcnow()
                db.session.commit()

                log = AnalysisLog(
                    user_id=user_id,
                    analysis_id=analysis_id,
                    action="analysis_failed",
                    details={"error": str(e)}
                )

                db.session.add(log)
                db.session.commit()


# ==========================================================
# START ANALYSIS
# ==========================================================

@analysis_bp.route("/start", methods=["POST"])
@jwt_required()
def start_analysis():

    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get("document_id"):
        return jsonify({"error": "Missing document_id"}), 400

    document = Document.query.filter_by(
        id=data["document_id"],
        user_id=user_id
    ).first()

    if not document:
        return jsonify({"error": "Document not found"}), 404

    # Prevent duplicate processing
    existing_analysis = (
        Analysis.query.filter_by(document_id=document.id)
        .filter(Analysis.status.in_(["processing", "completed"]))
        .first()
    )

    if existing_analysis:
        return jsonify({
            "message": "Analysis already in progress or completed",
            "analysis": existing_analysis.to_dict()
        }), 409

    try:
        analysis = Analysis(
            document_id=document.id,
            user_id=user_id,
            overall_similarity=0.0,
            ai_generated_probability=0.0,
            status="pending"
        )

        db.session.add(analysis)
        db.session.commit()

        # Log start
        log = AnalysisLog(
            user_id=user_id,
            analysis_id=analysis.id,
            action="analysis_started",
            details={"document_id": document.id}
        )

        db.session.add(log)
        db.session.commit()

        # Run in background thread
        thread = threading.Thread(
            target=run_analysis,
            args=(
                current_app._get_current_object(),
                analysis.id,
                document.id,
                user_id
            ),
            daemon=True
        )
        thread.start()

        return jsonify({
            "message": "Analysis started",
            "analysis": analysis.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"Error starting analysis: {str(e)}"
        }), 500


# ==========================================================
# CHECK STATUS
# ==========================================================

@analysis_bp.route("/status/<analysis_id>", methods=["GET"])
@jwt_required()
def check_analysis_status(analysis_id):

    user_id = get_jwt_identity()

    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=user_id
    ).first()

    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    return jsonify(analysis.to_dict()), 200


# ==========================================================
# LIST ANALYSES
# ==========================================================

@analysis_bp.route("/list", methods=["GET"])
@jwt_required()
def list_analyses():

    user_id = get_jwt_identity()

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    analyses = (
        Analysis.query
        .filter_by(user_id=user_id)
        .order_by(Analysis.created_at.desc())
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    return jsonify({
        "analyses": [a.to_dict() for a in analyses.items],
        "total": analyses.total,
        "pages": analyses.pages,
        "current_page": page
    }), 200
