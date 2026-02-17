from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models import Document, AnalysisLog
from app.services.file_processor import FileProcessor
from app.utils.validators import allowed_file
import os
import hashlib

upload_bp = Blueprint('upload', __name__)
file_processor = FileProcessor()

@upload_bp.route('/document', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload and process a document"""
    user_id = get_jwt_identity()
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed types: {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'}), 400
    
    try:
        # Create uploads directory
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Generate secure filename
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{hashlib.sha256(os.urandom(16)).hexdigest()}.{file_ext}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Extract text
        extracted_text = file_processor.extract_text(file_path, file_ext)
        
        if not extracted_text or len(extracted_text.strip()) == 0:
            os.remove(file_path)
            return jsonify({'error': 'No text content found in file'}), 400
        
        # Calculate content hash
        content_hash = hashlib.sha256(extracted_text.encode()).hexdigest()
        
        # Check for duplicate
        existing_doc = Document.query.filter_by(content_hash=content_hash, user_id=user_id).first()
        if existing_doc:
            os.remove(file_path)
            return jsonify({
                'message': 'Document already uploaded',
                'document': existing_doc.to_dict()
            }), 409
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create document record
        document = Document(
            user_id=user_id,
            filename=unique_filename,
            original_filename=filename,
            file_path=file_path,
            file_type=file_ext,
            file_size=file_size,
            content_hash=content_hash,
            extracted_text=extracted_text
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Log action
        log = AnalysisLog(
            user_id=user_id,
            action='document_uploaded',
            details={'document_id': document.id, 'filename': filename}
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        return jsonify({'error': f'File processing error: {str(e)}'}), 500

@upload_bp.route('/text', methods=['POST'])
@jwt_required()
def upload_text():
    """Upload plain text for analysis"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('text'):
        return jsonify({'error': 'No text provided'}), 400
    
    text = data['text'].strip()
    
    if len(text) < 50:
        return jsonify({'error': 'Text must be at least 50 characters'}), 400
    
    try:
        # Calculate content hash
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Check for duplicate
        existing_doc = Document.query.filter_by(content_hash=content_hash, user_id=user_id).first()
        if existing_doc:
            return jsonify({
                'message': 'Text already analyzed',
                'document': existing_doc.to_dict()
            }), 409
        
        # Create document record
        document = Document(
            user_id=user_id,
            filename=f"text_{hashlib.md5(os.urandom(16)).hexdigest()}.txt",
            original_filename=data.get('title', 'Untitled Text'),
            file_path='',
            file_type='txt',
            file_size=len(text),
            content_hash=content_hash,
            extracted_text=text
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Log action
        log = AnalysisLog(
            user_id=user_id,
            action='text_submitted',
            details={'document_id': document.id}
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'Text submitted successfully',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error processing text: {str(e)}'}), 500

@upload_bp.route('/documents', methods=['GET'])
@jwt_required()
def list_documents():
    """List all user documents"""
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    documents = Document.query.filter_by(user_id=user_id).order_by(Document.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'documents': [doc.to_dict() for doc in documents.items],
        'total': documents.total,
        'pages': documents.pages,
        'current_page': page
    }), 200

@upload_bp.route('/document/<doc_id>', methods=['GET'])
@jwt_required()
def get_document(doc_id):
    """Get document details"""
    user_id = get_jwt_identity()
    document = Document.query.filter_by(id=doc_id, user_id=user_id).first()
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    doc_data = document.to_dict()
    doc_data['text'] = document.extracted_text[:1000] + '...' if len(document.extracted_text) > 1000 else document.extracted_text
    
    return jsonify(doc_data), 200

@upload_bp.route('/document/<doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document(doc_id):
    """Delete a document"""
    user_id = get_jwt_identity()
    document = Document.query.filter_by(id=doc_id, user_id=user_id).first()
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    try:
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'message': 'Document deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting document: {str(e)}'}), 500