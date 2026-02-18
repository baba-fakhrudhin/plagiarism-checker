from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Analysis, Document, PlagiarismMatch

results_bp = Blueprint("results", __name__)


# ==========================================================
# GET FULL ANALYSIS RESULT
# ==========================================================

@results_bp.route("/analysis/<analysis_id>", methods=["GET"])
@jwt_required()
def get_analysis_results(analysis_id):

    user_id = get_jwt_identity()

    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=user_id
    ).first()

    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    if analysis.status != "completed":
        return jsonify({
            "error": f"Analysis status is '{analysis.status}'"
        }), 400

    document = db.session.get(Document, analysis.document_id)

    if not document:
        return jsonify({"error": "Associated document not found"}), 404

    matches = PlagiarismMatch.query.filter_by(
        analysis_id=analysis_id
    ).order_by(PlagiarismMatch.start_index.asc()).all()

    highlighted_segments = [
        {
            "start": match.start_index,
            "end": match.end_index,
            "type": match.match_type,
            "similarity": match.similarity_score,
            "source_url": match.source_url,
            "source_title": match.source_title,
        }
        for match in matches
    ]

    return jsonify({
        "analysis": analysis.to_dict(),
        "document": {
            "id": document.id,
            "filename": document.original_filename,
            "content": document.extracted_text[:50000]  # safety limit
        },
        "overall_similarity": analysis.overall_similarity,
        "ai_generated_probability": analysis.ai_generated_probability,
        "processing_time": analysis.processing_time,
        "total_matches": len(matches),
        "highlighted_segments": highlighted_segments,
        "matches": [match.to_dict() for match in matches]
    }), 200


# ==========================================================
# GET MATCHES WITH FILTERS & PAGINATION
# ==========================================================

@results_bp.route("/analysis/<analysis_id>/matches", methods=["GET"])
@jwt_required()
def get_matches(analysis_id):

    user_id = get_jwt_identity()

    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=user_id
    ).first()

    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    match_type = request.args.get("type")
    similarity_min = request.args.get("min_similarity", 0.5, type=float)
    sort_by = request.args.get("sort_by", "similarity")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = PlagiarismMatch.query.filter_by(
        analysis_id=analysis_id
    )

    if match_type:
        query = query.filter_by(match_type=match_type)

    query = query.filter(
        PlagiarismMatch.similarity_score >= similarity_min
    )

    if sort_by == "position":
        query = query.order_by(PlagiarismMatch.start_index.asc())
    else:
        query = query.order_by(PlagiarismMatch.similarity_score.desc())

    paginated = query.paginate(
        page=page,
        per_page=min(per_page, 100),
        error_out=False
    )

    return jsonify({
        "total_matches": paginated.total,
        "page": page,
        "pages": paginated.pages,
        "matches": [match.to_dict() for match in paginated.items]
    }), 200


# ==========================================================
# EXPORT RESULTS (JSON)
# ==========================================================

@results_bp.route("/analysis/<analysis_id>/export", methods=["GET"])
@jwt_required()
def export_results(analysis_id):

    user_id = get_jwt_identity()

    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=user_id
    ).first()

    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    if analysis.status != "completed":
        return jsonify({"error": "Analysis not completed yet"}), 400

    document = db.session.get(Document, analysis.document_id)

    if not document:
        return jsonify({"error": "Associated document not found"}), 404

    matches = PlagiarismMatch.query.filter_by(
        analysis_id=analysis_id
    ).all()

    export_data = {
        "analysis": analysis.to_dict(),
        "document": document.to_dict(),
        "overall_similarity": analysis.overall_similarity,
        "ai_generated_probability": analysis.ai_generated_probability,
        "processing_time": analysis.processing_time,
        "total_matches": len(matches),
        "matches": [match.to_dict() for match in matches]
    }

    return jsonify(export_data), 200
