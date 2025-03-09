# app/routes.py
"""
Routes module for the Yahoo Finance API application.
Defines all API endpoints and their handlers.
"""

from flask import Blueprint, request, jsonify, render_template
from app.services import (
    get_company_info, 
    get_historical_data, 
    get_company_news, 
    analyze_financial_data,
    analyze_historical_data
)
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint for API routes
api_bp = Blueprint('api', __name__)

@api_bp.route('/')
def home():
    """Homepage with forms for each endpoint."""
    return render_template('home.html')

@api_bp.route('/company')
def company_endpoint():
    """
    Endpoint for company information.
    
    Returns basic information about a company based on its stock symbol.
    
    Query Parameters:
        symbol (str): The stock symbol of the company (e.g., 'AAPL')
        
    Returns:
        JSON response with company information or error message
    """
    symbol = request.args.get('symbol', '')
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    
    try:
        result = get_company_info(symbol)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in company endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/news')
def news_endpoint():
    """
    Endpoint for company news.
    
    Returns recent news articles related to a company.
    
    Query Parameters:
        symbol (str): The stock symbol of the company (e.g., 'AAPL')
        
    Returns:
        JSON response with news articles or error message
    """
    symbol = request.args.get('symbol', '')
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    
    try:
        result = get_company_news(symbol)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in news endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/historical', methods=['POST'])
def historical_endpoint():
    """
    Endpoint for historical market data.
    
    Returns historical stock price data for a company within a specified date range.
    
    JSON Payload:
        symbol (str): The stock symbol of the company (e.g., 'AAPL')
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        JSON response with historical data or error message
    """
    data = request.json or {}
    
    symbol = data.get('symbol', '')
    start_date = data.get('start_date', '')
    end_date = data.get('end_date', '')
    
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    
    if not start_date or not end_date:
        return jsonify({"error": "Both start_date and end_date are required"}), 400
    
    try:
        result = get_historical_data(symbol, start_date, end_date)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in historical endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/analyze-financials', methods=['GET', 'POST'])
def analyze_financials_endpoint():
    """
    Endpoint for financial data analysis.
    
    Analyzes a company's financial statements and metrics.
    
    Query Parameters:
        symbol (str): The stock symbol of the company (e.g., 'AAPL')
        
    Returns:
        JSON response with financial analysis or error message
    """
    # Get symbol from either GET parameters or POST JSON
    if request.method == 'POST':
        data = request.get_json() or {}
        symbol = data.get('symbol', '')
    else:
        symbol = request.args.get('symbol', '')
        
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    
    try:
        # Call the service function to analyze financial data
        result = analyze_financial_data(symbol)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in analyze-financials endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/analyze-historical', methods=['POST'])
def analyze_historical_endpoint():
    """
    Endpoint for analyzing historical market data.
    
    Performs technical analysis on historical stock price data.
    
    JSON Payload:
        symbol (str): The stock symbol of the company (e.g., 'AAPL')
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        JSON response with analysis results or error message
    """
    data = request.json or {}
    
    symbol = data.get('symbol', '')
    start_date = data.get('start_date', '')
    end_date = data.get('end_date', '')
    
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    
    if not start_date or not end_date:
        return jsonify({"error": "Both start_date and end_date are required"}), 400
    
    try:
        # First, get the historical data
        historical_data = get_historical_data(symbol, start_date, end_date)
        
        # Then, analyze the data
        analysis = analyze_historical_data(historical_data)
        
        # Return both the raw data and the analysis
        result = {
            "historical_data": historical_data,
            "analysis": analysis
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in analyze-historical endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500