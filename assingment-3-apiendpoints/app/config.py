"""
Configuration module for the Yahoo Finance API application.

This module defines configuration classes for different environments
(development, production, testing) and provides a configuration dictionary
for easy access to the appropriate settings.

Environment-specific settings can be customized by setting environment variables
or by modifying the respective configuration class.
"""

import os

class Config:
    """
    Base configuration class with common settings.
    
    This class defines default configuration values that are common across
    all environments. Specific environments can override these values
    by extending this class.
    
    Attributes:
        DEBUG (bool): Flask debug mode flag, disabled by default
        TESTING (bool): Flask testing mode flag, disabled by default
        SECRET_KEY (str): Secret key for session security, fetched from environment
                         or uses a default value for development
        PORT (int): Port number for the server to listen on, defaults to 5000
    """
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    PORT = int(os.environ.get('PORT', 5000))
    
class DevelopmentConfig(Config):
    """
    Development environment configuration.
    
    Extends the base configuration with development-specific settings.
    Enables debug mode for detailed error messages and auto-reloading.
    
    Attributes:
        DEBUG (bool): Enabled for development environment
    """
    DEBUG = True
    
class ProductionConfig(Config):
    """
    Production environment configuration.
    
    Extends the base configuration with production-specific settings.
    Ensures debug mode is disabled for security and performance.
    
    Attributes:
        DEBUG (bool): Disabled for production environment
    """
    DEBUG = False
    # In production, the SECRET_KEY should be set as an environment variable
    
class TestingConfig(Config):
    """
    Testing environment configuration.
    
    Extends the base configuration with testing-specific settings.
    Enables testing mode for test runners and disables certain security features.
    
    Attributes:
        TESTING (bool): Enabled for testing environment
    """
    TESTING = True
    DEBUG = True
    
# Configuration dictionary for easy access to the appropriate config
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig  # Default configuration if not specified
}

# Active configuration can be selected using the FLASK_ENV environment variable
# or by directly accessing the appropriate configuration from the dictionary