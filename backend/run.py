import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create Flask application
app = create_app(os.getenv("CONFIG_NAME", "production"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "False") == "True"

    print("===================================")
    print(f"Starting Flask server on port {port}")
    print(f"Environment: {os.getenv('CONFIG_NAME', 'production')}")
    print(f"Debug mode: {debug}")
    print("===================================")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )
