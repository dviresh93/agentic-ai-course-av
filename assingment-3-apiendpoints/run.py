"""
Application entry point for the Yahoo Finance API server.

This module initializes and runs the Flask application with proper configuration
and logging. It also provides information about available endpoints and handles
SSL configuration for secure connections.

Usage:
    python run.py
"""

import logging
import os
from app import create_app
from app.config import config

# Configure logging with timestamp, logger name, and log level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the environment from an environment variable, defaulting to 'default'
env = os.environ.get('FLASK_ENV', 'default')
# Get the appropriate configuration class
config_class = config[env]

# Create the Flask application instance
app = create_app(env)

def main():
    """
    Main entry point of the application.
    
    Initializes the server, logs available endpoints, configures SSL if certificates
    are available, and starts the Flask development server.
    """
    logger.info("Starting Yahoo Finance API server")
    
    # Define and log available API endpoints for documentation purposes
    endpoints = [
        ("GET", "/", "Homepage with interactive forms"),
        ("GET", "/company?symbol=SYMBOL", "Get company information including sector, industry, and key metrics"),
        ("GET", "/historical?symbol=SYMBOL&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD", "Get historical price data (GET method)"),
        ("POST", "/historical", "Get historical price data with JSON payload (POST method)"),
        ("GET", "/news?symbol=SYMBOL", "Get latest company news articles"),
        ("GET", "/financials?symbol=SYMBOL", "Get financial statements and analysis"),
        ("POST", "/analyze-historical", "Analyze historical price data for trends and insights")
    ]
    
    logger.info("Available endpoints:")
    for method, path, desc in endpoints:
        logger.info(f"{method} {path} - {desc}")
    
    # Check for SSL certificates to enable HTTPS
    cert_path = os.path.join(os.path.dirname(__file__), 'cert.pem')
    key_path = os.path.join(os.path.dirname(__file__), 'key.pem')
    
    ssl_context = None
    if os.path.exists(cert_path) and os.path.exists(key_path):
        logger.info("SSL certificates found, enabling HTTPS")
        ssl_context = (cert_path, key_path)
    else:
        logger.warning("SSL certificates not found, running in HTTP mode")
    
    # Run the Flask application with the appropriate configuration
    # Note: Debug mode should be disabled in production
    app.run(
        host='0.0.0.0',  # Make server accessible from any network interface
        debug=config_class.DEBUG,  # Use debug setting from config class
        port=config_class.PORT,  # Use port from config class, defaulting to 5000
        ssl_context=ssl_context  # Apply SSL context if available
    )

if __name__ == "__main__":
    # Only run the application if this file is executed directly
    main()