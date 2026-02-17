from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Analysis, Document, PlagiarismMatch

results_bp = Blueprint('results', __name__)

@results_bp.route('/analysis/<analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis_results(analysis_id):
    """Get detailed analysis results"""
    user_id = get_jwt_identity()
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    if analysis.status != 'completed':
        return jsonify({'error': f'Analysis status is {analysis.status}'}), 400
    
    document = Document.query.get(analysis.document_id)
    matches = PlagiarismMatch.query.filter_by(analysis_id=analysis_id).all()
    
    # Build highlighted text with match indices
    highlighted_segments = []
    for match in sorted(matches, key=lambda m: m.start_index):
        highlighted_segments.append({
            'start': match.start_index,
            'end': match.end_index,
            'type': match.match_type,
            'similarity': match.similarity_score,
            'source_url': match.source_url,
            'source_title': match.source_title
        })
    
    return jsonify({
        'analysis': analysis.to_dict(),
        'document': {
            'id': document.id,
            'filename': document.original_filename,
            'content': document.extracted_text
        },
        'overall_similarity': analysis.overall_similarity,
        'ai_generated_probability': analysis.ai_generated_probability,
        'total_matches': len(matches),
        'highlighted_segments': highlighted_segments,
        'matches': [match.to_dict() for match in matches]
    }), 200

@results_bp.route('/analysis/<analysis_id>/matches', methods=['GET'])
@jwt_required()
def get_matches(analysis_id):
    """Get plagiarism matches for an analysis"""
    user_id = get_jwt_identity()
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    match_type = request.args.get('type')
    similarity_min = request.args.get('min_similarity', 0.5, type=float)
    sort_by = request.args.get('sort_by', 'similarity')
    
    query = PlagiarismMatch.query.filter_by(analysis_id=analysis_id)
    
    if match_type:
        query = query.filter_by(match_type=match_type)
    
    query = query.filter(PlagiarismMatch.similarity_score >= similarity_min)
    
    if sort_by == 'similarity':
        query = query.order_by(PlagiarismMatch.similarity_score.desc())
    elif sort_by == 'position':
        query = query.order_by(PlagiarismMatch.start_index.asc())
    
    matches = query.all()
    
    return jsonify({
        'total_matches': len(matches),
        'matches': [match.to_dict() for match in matches]
    }), 200

@results_bp.route('/analysis/<analysis_id>/export', methods=['GET'])
@jwt_required()
def export_results(analysis_id):
    """Export analysis results as JSON"""
    user_id = get_jwt_identity()
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    document = Document.query.get(analysis.document_id)
    matches = PlagiarismMatch.query.filter_by(analysis_id=analysis_id).all()
    
    export_data = {
        'analysis': analysis.to_dict(),
        'document': document.to_dict(),
        'overall_similarity': analysis.overall_similarity,
        'ai_generated_probability': analysis.ai_generated_probability,
        'processing_time': analysis.processing_time,
        'total_matches': len(matches),
        'matches': [match.to_dict() for match in matches]
    }
    
    return jsonify(export_data), 200