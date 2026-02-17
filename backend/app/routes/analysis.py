from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Document, Analysis, PlagiarismMatch, AnalysisLog
from app.services.plagiarism_detector import PlagiarismDetector
from app.services.ai_detector import AIDetector
from datetime import datetime
import time
import threading

analysis_bp = Blueprint('analysis', __name__)
plagiarism_detector = PlagiarismDetector()
ai_detector = AIDetector()

def run_analysis(analysis_id, document_id, user_id):
    """Background task for running plagiarism analysis"""
    try:
        analysis = Analysis.query.get(analysis_id)
        document = Document.query.get(document_id)
        
        if not analysis or not document:
            return
        
        analysis.status = 'processing'
        db.session.commit()
        
        start_time = time.time()
        
        # Run plagiarism detection
        matches = plagiarism_detector.detect_plagiarism(document.extracted_text)
        
        # Run AI detection
        ai_probability = ai_detector.detect_ai_generated(document.extracted_text)
        
        # Calculate overall similarity
        overall_similarity = max([m.similarity_score for m in matches]) if matches else 0.0
        
        # Add matches to analysis
        for match in matches:
            match.analysis_id = analysis_id
            db.session.add(match)
        
        # Update analysis
        analysis.overall_similarity = overall_similarity
        analysis.ai_generated_probability = ai_probability
        analysis.status = 'completed'
        analysis.completed_at = datetime.utcnow()
        analysis.processing_time = time.time() - start_time
        
        db.session.commit()
        
        # Log completion
        log = AnalysisLog(
            user_id=user_id,
            analysis_id=analysis_id,
            action='analysis_completed',
            details={
                'similarity': overall_similarity,
                'ai_probability': ai_probability,
                'match_count': len(matches)
            }
        )
        db.session.add(log)
        db.session.commit()
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        analysis = Analysis.query.get(analysis_id)
        if analysis:
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.completed_at = datetime.utcnow()
            db.session.commit()
            
            log = AnalysisLog(
                user_id=user_id,
                analysis_id=analysis_id,
                action='analysis_failed',
                details={'error': str(e)}
            )
            db.session.add(log)
            db.session.commit()

@analysis_bp.route('/start', methods=['POST'])
@jwt_required()
def start_analysis():
    """Start plagiarism analysis for a document"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('document_id'):
        return jsonify({'error': 'Missing document_id'}), 400
    
    document = Document.query.filter_by(id=data['document_id'], user_id=user_id).first()
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Check if analysis already exists and is not failed
    existing_analysis = Analysis.query.filter_by(document_id=document.id).filter(
        Analysis.status.in_(['processing', 'completed'])
    ).first()
    
    if existing_analysis:
        return jsonify({
            'message': 'Analysis already in progress or completed',
            'analysis': existing_analysis.to_dict()
        }), 409
    
    try:
        analysis = Analysis(
            document_id=document.id,
            user_id=user_id,
            overall_similarity=0.0,
            status='pending'
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Log action
        log = AnalysisLog(
            user_id=user_id,
            analysis_id=analysis.id,
            action='analysis_started',
            details={'document_id': document.id}
        )
        db.session.add(log)
        db.session.commit()
        
        # Run analysis in background thread
        thread = threading.Thread(
            target=run_analysis,
            args=(analysis.id, document.id, user_id),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'message': 'Analysis started',
            'analysis': analysis.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error starting analysis: {str(e)}'}), 500

@analysis_bp.route('/status/<analysis_id>', methods=['GET'])
@jwt_required()
def check_analysis_status(analysis_id):
    """Check analysis status"""
    user_id = get_jwt_identity()
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    return jsonify(analysis.to_dict()), 200

@analysis_bp.route('/list', methods=['GET'])
@jwt_required()
def list_analyses():
    """List all user analyses"""
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    analyses = Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'analyses': [analysis.to_dict() for analysis in analyses.items],
        'total': analyses.total,
        'pages': analyses.pages,
        'current_page': page
    }), 200