import os
from dotenv import load_dotenv
from app import create_app, db

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Context for Flask shell"""
    return {'db': db}

@app.before_request
def log_request():
    """Log incoming requests"""
    import logging
    logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False') == 'True'
    
    print(f"Starting Flask server on port {port}...")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )