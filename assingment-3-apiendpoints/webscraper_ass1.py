from flask import Flask, request, jsonify, render_template_string
import yfinance as yf
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML template for the homepage
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Yahoo Finance API</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        .endpoint { background: #f5f5f5; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
        .endpoint h2 { margin-top: 0; }
        form { margin-top: 10px; }
        label, input, button { margin: 5px; }
        button { background: #4CAF50; color: white; border: none; padding: 8px 16px; cursor: pointer; border-radius: 4px; }
        pre { background: #f9f9f9; padding: 10px; border-radius: 4px; overflow-x: auto; }
    </style>
    <script>
        function submitHistoricalForm(event) {
            event.preventDefault();
            const form = event.target;
            const symbol = form.querySelector('#symbol2').value;
            const startDate = form.querySelector('#start_date').value;
            const endDate = form.querySelector('#end_date').value;
            
            fetch('/historical', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    start_date: startDate,
                    end_date: endDate
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('historical-result').textContent = JSON.stringify(data, null, 2);
            })
            .catch(error => {
                document.getElementById('historical-result').textContent = 'Error: ' + error;
            });
        }
    </script>
</head>
<body>
    <h1>Yahoo Finance API</h1>
    
    <div class="endpoint">
        <h2>Company Information</h2>
        <form action="/company" method="get">
            <label for="symbol1">Company Symbol:</label>
            <input type="text" id="symbol1" name="symbol" required placeholder="AAPL">
            <button type="submit">Get Info</button>
        </form>
    </div>
    
    <div class="endpoint">
        <h2>Historical Data</h2>
        <form onsubmit="submitHistoricalForm(event)">
            <label for="symbol2">Company Symbol:</label>
            <input type="text" id="symbol2" name="symbol" required placeholder="AAPL">
            <label for="start_date">Start Date:</label>
            <input type="date" id="start_date" name="start_date" required>
            <label for="end_date">End Date:</label>
            <input type="date" id="end_date" name="end_date" required>
            <button type="submit">Get History</button>
        </form>
        <pre id="historical-result"></pre>
    </div>
    
    <div class="endpoint">
        <h2>Company News</h2>
        <form action="/news" method="get">
            <label for="symbol3">Company Symbol:</label>
            <input type="text" id="symbol3" name="symbol" required placeholder="AAPL">
            <button type="submit">Get News</button>
        </form>
    </div>
    
    <div class="endpoint">
        <h2>Financial Data</h2>
        <form action="/financials" method="get">
            <label for="symbol4">Company Symbol:</label>
            <input type="text" id="symbol4" name="symbol" required placeholder="AAPL">
            <button type="submit">Get Financials</button>
        </form>
    </div>
</body>
</html>
"""

# ---- Business Logic Functions ----

def get_company_info(symbol):
    """Get basic company information."""
    logger.info(f"Fetching company info for {symbol}")
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        return {
            "symbol": symbol,
            "name": info.get('shortName', 'N/A'),
            "price": info.get('currentPrice', 'N/A'),
            "marketCap": info.get('marketCap', 'N/A'),
            "description": info.get('longBusinessSummary', 'N/A')
        }
    except Exception as e:
        logger.error(f"Error fetching company info: {str(e)}")
        raise

def get_historical_data(symbol, start_date=None, end_date=None):
    """Get historical price data for a company within a date range."""
    logger.info(f"Fetching historical data for {symbol} from {start_date} to {end_date}")
    try:
        stock = yf.Ticker(symbol)
        
        # Parse date strings to datetime objects if they're strings
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
        # If end_date is today, add one day to include today's data
        if end_date.date() == datetime.now().date():
            end_date = end_date + timedelta(days=1)
        
        history = stock.history(start=start_date, end=end_date)
        
        # Convert the data to a format suitable for JSON
        result = []
        for date, row in history.iterrows():
            result.append({
                "date": date.strftime('%Y-%m-%d'),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return {
            "symbol": symbol,
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error fetching historical data: {str(e)}")
        raise

def get_company_news(symbol):
    """Get latest news for a company."""
    logger.info(f"Fetching news for {symbol}")
    try:
        stock = yf.Ticker(symbol)
        news = stock.news
        
        # Format the news
        formatted_news = []
        for item in news[:5]:  # Limit to 5 news items
            formatted_news.append({
                "title": item.get('title', 'No title'),
                "publisher": item.get('publisher', 'Unknown'),
                "link": item.get('link', '#'),
                "published": datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return {
            "symbol": symbol,
            "news_count": len(formatted_news),
            "news": formatted_news
        }
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise

def get_financial_data(symbol):
    """Get financial statement data for a company."""
    logger.info(f"Fetching financial data for {symbol}")
    try:
        stock = yf.Ticker(symbol)
        
        # Get income statement, balance sheet, and cash flow
        income_stmt = stock.income_stmt
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
        
        # Extract the most recent data
        latest_income = {}
        if not income_stmt.empty:
            latest_income = income_stmt.iloc[:, 0].to_dict()
            # Convert numpy values to native Python types for JSON serialization
            latest_income = {k: float(v) if hasattr(v, 'item') else v for k, v in latest_income.items()}
        
        latest_balance = {}
        if not balance_sheet.empty:
            latest_balance = balance_sheet.iloc[:, 0].to_dict()
            latest_balance = {k: float(v) if hasattr(v, 'item') else v for k, v in latest_balance.items()}
        
        latest_cashflow = {}
        if not cash_flow.empty:
            latest_cashflow = cash_flow.iloc[:, 0].to_dict()
            latest_cashflow = {k: float(v) if hasattr(v, 'item') else v for k, v in latest_cashflow.items()}
        
        return {
            "symbol": symbol,
            "income_statement": latest_income,
            "balance_sheet": latest_balance,
            "cash_flow": latest_cashflow
        }
    except Exception as e:
        logger.error(f"Error fetching financial data: {str(e)}")
        raise

# ---- Flask Routes ----

@app.route('/')
def home():
    """Homepage with forms for each endpoint."""
    return render_template_string(HOME_TEMPLATE)

@app.route('/company')
def company_endpoint():
    """Endpoint for basic company information."""
    symbol = request.args.get('symbol', '')
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    
    try:
        result = get_company_info(symbol)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/historical', methods=['GET', 'POST'])
def historical_endpoint():
    """Endpoint for historical price data. Supports both GET and POST methods."""
    try:
        # Handle POST request with JSON payload
        if request.method == 'POST':
            data = request.json
            if not data:
                return jsonify({"error": "Missing JSON payload"}), 400
                
            symbol = data.get('symbol')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
        # Handle GET request with query parameters (keeping for backward compatibility)
        else:
            symbol = request.args.get('symbol', '')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
        
        # Validate required parameters
        if not symbol:
            return jsonify({"error": "Symbol is required"}), 400
            
        if not start_date or not end_date:
            return jsonify({"error": "Both start_date and end_date are required"}), 400
            
        # Parse dates to ensure they're valid
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Check if start date is before end date
            if start_date_obj > end_date_obj:
                return jsonify({"error": "Start date must be before end date"}), 400
                
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        result = get_historical_data(symbol, start_date, end_date)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/news')
def news_endpoint():
    """Endpoint for company news."""
    symbol = request.args.get('symbol', '')
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    
    try:
        result = get_company_news(symbol)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/financials')
def financials_endpoint():
    """Endpoint for financial data."""
    symbol = request.args.get('symbol', '')
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    
    try:
        result = get_financial_data(symbol)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---- Main Entry Point ----

def main():
    """Main entry point of the application."""
    logger.info("Starting Yahoo Finance API server")
    
    # Log available endpoints
    endpoints = [
        ("GET", "/", "Homepage with forms"),
        ("GET", "/company?symbol=SYMBOL", "Get company information"),
        ("GET", "/historical?symbol=SYMBOL&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD", "Get historical price data (GET)"),
        ("POST", "/historical", "Get historical price data with JSON payload (POST)"),
        ("GET", "/news?symbol=SYMBOL", "Get company news"),
        ("GET", "/financials?symbol=SYMBOL", "Get financial data")
    ]
    
    logger.info("Available endpoints:")
    for method, path, desc in endpoints:
        logger.info(f"{method} {path} - {desc}")
    
    # Run the Flask application
    app.run(debug=True, port=5000)

if __name__ == '__main__':
    main()