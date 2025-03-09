"""
Services module for the Yahoo Finance API application.

This module provides functions for fetching and analyzing financial data from Yahoo Finance.
It includes functionality for retrieving company information, historical price data,
news articles, and performing financial and technical analysis.

Dependencies:
    - yfinance: For fetching financial data from Yahoo Finance
    - pandas: For data manipulation and analysis
    - numpy: For numerical operations
    - datetime: For date handling
    - logging: For application logging
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

def get_company_info(symbol):
    """
    Get basic information about a company.
    
    Retrieves company profile, sector, industry, and key financial metrics
    from Yahoo Finance based on the provided stock symbol.
    
    Args:
        symbol (str): The stock symbol of the company (e.g., 'AAPL')
        
    Returns:
        dict: Company information including name, sector, industry, etc.
        
    Raises:
        Exception: If there's an error fetching the data
    """
    logger.info(f"Fetching company info for {symbol}")
    try:
        # Create a Ticker object for the specified symbol
        stock = yf.Ticker(symbol)
        info = stock.info
        
        # Extract relevant information and handle missing data with 'N/A'
        return {
            "symbol": symbol,
            "name": info.get('shortName', 'N/A'),
            "sector": info.get('sector', 'N/A'),
            "industry": info.get('industry', 'N/A'),
            "country": info.get('country', 'N/A'),
            "website": info.get('website', 'N/A'),
            "market_cap": info.get('marketCap', 'N/A'),
            "current_price": info.get('currentPrice', 'N/A'),
            "52_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
            "52_week_low": info.get('fiftyTwoWeekLow', 'N/A')
        }
    except Exception as e:
        logger.error(f"Error fetching company info: {str(e)}")
        raise

def get_historical_data(symbol, start_date, end_date):
    """
    Get historical market data for a company within a specified date range.
    
    Retrieves daily price data (open, high, low, close) and volume for the
    specified company and date range.
    
    Args:
        symbol (str): The stock symbol of the company (e.g., 'AAPL')
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
        
    Returns:
        dict: Historical price data including open, high, low, close, and volume
        
    Raises:
        Exception: If there's an error fetching the data
    """
    logger.info(f"Fetching historical data for {symbol} from {start_date} to {end_date}")
    try:
        # Create a Ticker object and fetch historical data
        stock = yf.Ticker(symbol)
        history = stock.history(start=start_date, end=end_date)
        
        # Format the data into a list of dictionaries for easier JSON serialization
        data = []
        for index, row in history.iterrows():
            data.append({
                "date": index.strftime('%Y-%m-%d'),
                "open": row['Open'],
                "high": row['High'],
                "low": row['Low'],
                "close": row['Close'],
                "volume": row['Volume']
            })
        
        # Return formatted data with metadata
        return {
            "symbol": symbol,
            "period": f"{start_date} to {end_date}",
            "data_count": len(data),
            "data": data
        }
    except Exception as e:
        logger.error(f"Error fetching historical data: {str(e)}")
        raise

def get_company_news(symbol):
    """
    Retrieve news articles for a given company symbol.
    
    Args:
        symbol (str): The stock symbol of the company (e.g., 'AAPL')
        
    Returns:
        dict: News articles and metadata
    """
    logger.info(f"Retrieving news for {symbol}")
    
    try:
        # Create a Ticker object
        ticker = yf.Ticker(symbol)
        
        # Get news data
        news_data = ticker.news
        
        # Debug the news data structure
        logger.info(f"Retrieved {len(news_data)} news items")
        if news_data and len(news_data) > 0:
            logger.info(f"First news item keys: {news_data[0].keys()}")
            logger.info(f"Sample news item: {news_data[0]}")
        
        # Process news items with better error handling
        processed_news = []
        for item in news_data:
            try:
                # Check if content field exists (new structure)
                content = item.get('content', {})
                
                # Extract title from either direct or nested structure
                title = item.get('title', None)
                if not title and isinstance(content, dict):
                    title = content.get('title', 'No title available')
                
                # Extract publisher info
                provider = content.get('provider', {}) if isinstance(content, dict) else {}
                publisher = provider.get('displayName', 'Unknown') if isinstance(provider, dict) else 'Unknown'
                
                # Extract publication date
                pub_date = 'Unknown date'
                if isinstance(content, dict) and content.get('pubDate'):
                    # Format ISO date string to readable format
                    try:
                        date_str = content.get('pubDate')
                        # Convert ISO format to datetime and then to string
                        dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                        pub_date = dt.strftime('%Y-%m-%d %H:%M')
                    except Exception as e:
                        logger.error(f"Error parsing date: {str(e)}")
                
                # Extract link
                link = '#'
                if isinstance(content, dict) and content.get('clickThroughUrl'):
                    click_url = content.get('clickThroughUrl')
                    if isinstance(click_url, dict):
                        link = click_url.get('url', '#')
                
                processed_news.append({
                    'title': title,
                    'publisher': publisher,
                    'published': pub_date,
                    'link': link
                })
                
                # Log successful processing
                logger.info(f"Processed news item: {title[:30]}... from {publisher}")
                
            except Exception as e:
                logger.error(f"Error processing news item: {str(e)}")
                logger.error(f"Problematic item: {item}")
        
        return {
            'symbol': symbol,
            'news_count': len(processed_news),
            'news': processed_news
        }
    except Exception as e:
        logger.error(f"Error retrieving news for {symbol}: {str(e)}")
        raise Exception(f"Failed to retrieve news: {str(e)}")

def analyze_financial_data(symbol):
    """
    Analyze financial data for a given company symbol.
    
    Retrieves and analyzes financial statements, calculates key ratios,
    and provides performance metrics and insights.
    
    Args:
        symbol (str): The stock symbol of the company (e.g., 'AAPL')
        
    Returns:
        dict: Financial analysis results including income statement, balance sheet,
              cash flow, key ratios, and performance metrics
    """
    logger.info(f"Analyzing financial data for {symbol}")
    
    try:
        # Create a Ticker object
        ticker = yf.Ticker(symbol)
        
        # Get financial data
        logger.info(f"Fetching financial statements for {symbol}")
        income_stmt = ticker.income_stmt
        balance_sheet = ticker.balance_sheet
        cash_flow = ticker.cashflow
        
        # Get company info for summary metrics
        info = ticker.info
        
        # Basic metrics - handle NaN values
        market_cap = info.get('marketCap', 'N/A')
        pe_ratio = info.get('trailingPE', 'N/A')
        if pd.isna(pe_ratio):
            pe_ratio = 'N/A'
            
        forward_pe = info.get('forwardPE', 'N/A')
        if pd.isna(forward_pe):
            forward_pe = 'N/A'
            
        dividend_yield = info.get('dividendYield', 'N/A')
        if pd.isna(dividend_yield):
            dividend_yield = 'N/A'
        elif dividend_yield != 'N/A':
            dividend_yield = f"{dividend_yield * 100:.2f}%"
        
        # Simplify the response to match expected format in the frontend
        return {
            "company": info.get('shortName', symbol),
            "symbol": symbol,
            "summary": {
                "Market Cap": market_cap,
                "P/E Ratio": pe_ratio,
                "Forward P/E": forward_pe,
                "Dividend Yield": dividend_yield,
                "52 Week High": info.get('fiftyTwoWeekHigh', 'N/A'),
                "52 Week Low": info.get('fiftyTwoWeekLow', 'N/A')
            },
            # Include simplified financial data
            "income_statement": "Available" if not income_stmt.empty else "Not available",
            "balance_sheet": "Available" if not balance_sheet.empty else "Not available",
            "cash_flow": "Available" if not cash_flow.empty else "Not available"
        }
    except Exception as e:
        logger.error(f"Error analyzing financial data for {symbol}: {str(e)}")
        return {
            "error": f"Failed to analyze financial data: {str(e)}",
            "symbol": symbol
        }

def analyze_historical_data(historical_data):
    """
    Analyze historical market data and provide actionable insights.
    
    Performs technical analysis on historical price data, including:
    - Price trend analysis
    - Moving average calculations
    - Volatility assessment
    - Volume analysis
    - Support and resistance levels
    
    Args:
        historical_data (dict): Dictionary containing historical price data
        
    Returns:
        dict: Analysis results including summary statistics, technical indicators,
              volume analysis, insights, and recommendations
    """
    logger.info("Analyzing historical market data")
    
    try:
        # Extract data from the historical_data dictionary
        symbol = historical_data.get('symbol', 'Unknown')
        period = historical_data.get('period', 'Unknown')
        data = historical_data.get('data', [])
        
        # Check if we have data to analyze
        if not data:
            return {
                "error": "No historical data available for analysis"
            }
        
        # Convert data to more usable format (lists of values)
        dates = []
        prices_close = []
        prices_open = []
        volumes = []
        
        for item in data:
            dates.append(item.get('date'))
            prices_close.append(item.get('close'))
            prices_open.append(item.get('open'))
            volumes.append(item.get('volume'))
        
        # Calculate basic price statistics
        latest_price = prices_close[0] if prices_close else None
        oldest_price = prices_close[-1] if prices_close else None
        highest_price = max(prices_close) if prices_close else None
        lowest_price = min(prices_close) if prices_close else None
        avg_price = sum(prices_close) / len(prices_close) if prices_close else None
        
        # Calculate price change over the period
        price_change = None
        price_change_pct = None
        
        if latest_price is not None and oldest_price is not None:
            price_change = latest_price - oldest_price
            price_change_pct = (price_change / oldest_price) * 100
        
        # Calculate moving averages if we have enough data points
        sma_20 = None
        sma_50 = None
        sma_200 = None
        
        if len(prices_close) >= 20:
            sma_20 = sum(prices_close[:20]) / 20
        
        if len(prices_close) >= 50:
            sma_50 = sum(prices_close[:50]) / 50
        
        if len(prices_close) >= 200:
            sma_200 = sum(prices_close[:200]) / 200
        
        # Calculate volatility (standard deviation of daily returns)
        volatility = None
        if len(prices_close) > 1:
            # Calculate daily percentage returns
            daily_returns = [(prices_close[i] / prices_close[i+1] - 1) * 100 for i in range(len(prices_close)-1)]
            volatility = np.std(daily_returns)  # Standard deviation of returns
        
        # Calculate volume statistics
        avg_volume = sum(volumes) / len(volumes) if volumes else None
        latest_volume = volumes[0] if volumes else None
        
        # Generate insights based on the analysis
        insights = []
        
        # Price trend insights
        if price_change is not None:
            if price_change > 0:
                insights.append(f"Bullish trend: Price increased by {price_change_pct:.2f}% over the period")
            else:
                insights.append(f"Bearish trend: Price decreased by {abs(price_change_pct):.2f}% over the period")
        
        # Volatility insights
        if volatility is not None:
            if volatility > 3:
                insights.append(f"High volatility: Daily price fluctuations of {volatility:.2f}% on average")
            elif volatility < 1:
                insights.append(f"Low volatility: Stable price movement with {volatility:.2f}% average daily change")
        
        # Moving average insights (trend identification)
        if sma_20 is not None and sma_50 is not None and latest_price is not None:
            if latest_price > sma_20 > sma_50:
                insights.append("Strong upward trend: Price above both 20-day and 50-day moving averages")
            elif latest_price < sma_20 < sma_50:
                insights.append("Strong downward trend: Price below both 20-day and 50-day moving averages")
            elif latest_price > sma_20 and sma_20 < sma_50:
                insights.append("Potential reversal: Price crossed above 20-day moving average")
            elif latest_price < sma_20 and sma_20 > sma_50:
                insights.append("Potential downtrend: Price crossed below 20-day moving average")
        
        # Volume insights (trading activity)
        if latest_volume is not None and avg_volume is not None:
            volume_ratio = latest_volume / avg_volume
            if volume_ratio > 1.5:
                insights.append("Increased trading activity: Recent volume is significantly above average")
            elif volume_ratio < 0.5:
                insights.append("Decreased trading activity: Recent volume is significantly below average")
        
        # Support and resistance levels (simplified approach)
        if highest_price is not None and lowest_price is not None:
            resistance = highest_price
            support = lowest_price
            insights.append(f"Key levels: Support at ${support:.2f}, resistance at ${resistance:.2f}")
        
        # Generate trading recommendations based on insights
        recommendations = []
        
        if insights:
            # Position recommendations based on trend
            if any("Bullish" in insight for insight in insights):
                recommendations.append("Consider long positions with appropriate risk management")
            elif any("Bearish" in insight for insight in insights):
                recommendations.append("Consider reducing exposure or implementing hedging strategies")
            
            # Risk management recommendations based on volatility
            if any("High volatility" in insight for insight in insights):
                recommendations.append("Use tighter stop-loss orders due to increased price volatility")
            
            # Momentum-based recommendations
            if any("Upward trend" in insight for insight in insights) and any("increased trading activity" in insight.lower() for insight in insights):
                recommendations.append("Strong buying momentum may indicate further upside potential")
            elif any("Downward trend" in insight for insight in insights) and any("increased trading activity" in insight.lower() for insight in insights):
                recommendations.append("Strong selling pressure may indicate further downside risk")
        
        # Compile all analysis results into a structured dictionary
        analysis_results = {
            "symbol": symbol,
            "period": period,
            "summary": {
                "latest_price": round(latest_price, 2) if latest_price is not None else None,
                "price_change": round(price_change, 2) if price_change is not None else None,
                "price_change_percent": round(price_change_pct, 2) if price_change_pct is not None else None,
                "highest_price": round(highest_price, 2) if highest_price is not None else None,
                "lowest_price": round(lowest_price, 2) if lowest_price is not None else None,
                "average_price": round(avg_price, 2) if avg_price is not None else None,
                "volatility": round(volatility, 2) if volatility is not None else None
            },
            "technical_indicators": {
                "sma_20": round(sma_20, 2) if sma_20 is not None else None,
                "sma_50": round(sma_50, 2) if sma_50 is not None else None,
                "sma_200": round(sma_200, 2) if sma_200 is not None else None
            },
            "volume_analysis": {
                "average_volume": int(avg_volume) if avg_volume is not None else None,
                "latest_volume": int(latest_volume) if latest_volume is not None else None,
                "volume_trend": "Above Average" if latest_volume > avg_volume else "Below Average" if latest_volume < avg_volume else "Average" if latest_volume is not None and avg_volume is not None else None
            },
            "insights": insights,
            "recommendations": recommendations
        }
        
        return analysis_results
    
    except Exception as e:
        # Log the error and return an error message
        logger.error(f"Error analyzing historical data: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}"}