from app import db
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    subscription_plan = db.Column(db.String(20), default='free')
    documents = db.relationship('Document', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'subscription_plan': self.subscription_plan,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    content_hash = db.Column(db.String(64), unique=True, index=True)
    extracted_text = db.Column(db.Text, nullable=False)
    page_count = db.Column(db.Integer)
    analyses = db.relationship('Analysis', backref='document', lazy='dynamic', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    overall_similarity = db.Column(db.Float, nullable=False, default=0.0)
    ai_generated_probability = db.Column(db.Float, nullable=True, default=0.0)
    plagiarism_matches = db.relationship('PlagiarismMatch', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')
    status = db.Column(db.String(20), default='pending', index=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    processing_time = db.Column(db.Float, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'overall_similarity': self.overall_similarity,
            'ai_generated_probability': self.ai_generated_probability,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'processing_time': self.processing_time
        }

class PlagiarismMatch(db.Model):
    __tablename__ = 'plagiarism_matches'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('analyses.id'), nullable=False, index=True)
    source_url = db.Column(db.String(500), nullable=True)
    source_title = db.Column(db.String(255), nullable=True)
    matched_text = db.Column(db.Text, nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    match_type = db.Column(db.String(20), nullable=False)
    start_index = db.Column(db.Integer, nullable=False)
    end_index = db.Column(db.Integer, nullable=False)
    source_start_index = db.Column(db.Integer, nullable=True)
    source_end_index = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_url': self.source_url,
            'source_title': self.source_title,
            'matched_text': self.matched_text,
            'original_text': self.original_text,
            'similarity_score': self.similarity_score,
            'match_type': self.match_type,
            'start_index': self.start_index,
            'end_index': self.end_index
        }

class AnalysisLog(db.Model):
    __tablename__ = 'analysis_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    analysis_id = db.Column(db.String(36), db.ForeignKey('analyses.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)