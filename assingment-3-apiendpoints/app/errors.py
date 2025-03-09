"""
Error handling module for the Yahoo Finance API application.

This module defines custom exception classes and error handlers for the API.
It ensures that all errors are properly caught and returned to the client
in a consistent JSON format with appropriate HTTP status codes.
"""

from flask import jsonify
from app.routes import api_bp

class APIError(Exception):
    """
    Base class for API-specific exceptions.
    
    This custom exception allows for consistent error handling across the application
    with control over both the error message and HTTP status code.
    
    Attributes:
        message (str): Human-readable error description
        status_code (int): HTTP status code to return (defaults to 400 Bad Request)
    """
    def __init__(self, message, status_code=400):
        """
        Initialize a new APIError.
        
        Args:
            message (str): Human-readable error description
            status_code (int, optional): HTTP status code. Defaults to 400 (Bad Request).
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

@api_bp.errorhandler(APIError)
def handle_api_error(error):
    """
    Error handler for APIError exceptions.
    
    Converts APIError exceptions into JSON responses with the appropriate
    error message and status code.
    
    Args:
        error (APIError): The exception that was raised
        
    Returns:
        Response: JSON response with error details and appropriate status code
    """
    response = jsonify({"error": error.message})
    response.status_code = error.status_code
    return response

@api_bp.errorhandler(Exception)
def handle_generic_error(error):
    """
    Fallback error handler for all unhandled exceptions.
    
    Catches any unhandled exceptions and returns them as JSON responses
    with a 500 Internal Server Error status code. This prevents exposing
    stack traces or technical details to the client.
    
    Args:
        error (Exception): The unhandled exception
        
    Returns:
        Response: JSON response with error message and 500 status code
    """
    response = jsonify({"error": str(error)})
    response.status_code = 500
    return response