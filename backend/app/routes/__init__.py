from .auth import auth_bp
from .upload import upload_bp
from .analysis import analysis_bp
from .results import results_bp

__all__ = ['auth_bp', 'upload_bp', 'analysis_bp', 'results_bp']