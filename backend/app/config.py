import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '9f3d8b2c6a1e4f7d9c2b5e8a6f1d3c7b9e2f4a6d8c1b3e5f7a9d2c6b8e1f3')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # File Upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'pptx', 'doc', 'ppt'}
    
    # Plagiarism Detection
    SIMILARITY_THRESHOLD = 0.7
    NGRAM_SIZE = 3
    
    # Web Scraping
    SCRAPER_MAX_RESULTS = 100
    SCRAPER_TIMEOUT = 30

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://plagiarism_user:bNnmGKr47d100oPy2xRzC9d3QLBWsj5w@dpg-d6af0l95pdvs73emjjhg-a/plagiarism_checker'
    )

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # Stricter settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = '9f3d8b2c6a1e4f7d9c2b5e8a6f1d3c7b9e2f4a6d8c1b3e5f7a9d2c6b8e1f3'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}