# app/__init__.py
from flask import Flask, render_template
from app.config import config
from app.routes import api_bp

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/')
    
    @app.route('/')
    def home():
        return render_template('home.html')
    
    return app