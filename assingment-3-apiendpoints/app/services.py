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
    Get recent news articles about a company.
    
    Retrieves news articles related to the specified company from Yahoo Finance.
    
    Args:
        symbol (str): The stock symbol of the company (e.g., 'AAPL')
        
    Returns:
        dict: News articles with title, publisher, date, and link
        
    Raises:
        Exception: If there's an error fetching the news
    """
    logger.info(f"Fetching news for {symbol}")
    try:
        # Create a Ticker object and fetch news data
        stock = yf.Ticker(symbol)
        news_data = stock.news
        
        # Format the news data
        news = []
        for item in news_data[:10]:  # Limit to 10 news items
            news.append({
                "title": item.get('title', 'No title'),
                "publisher": item.get('publisher', 'Unknown'),
                "published": datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M'),
                "link": item.get('link', '#')
            })
        
        return {
            "symbol": symbol,
            "news_count": len(news),
            "news": news
        }
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise

def analyze_financial_data(symbol):
    """
    Analyze financial data and calculate key metrics for a company.
    
    Retrieves financial statements (income statement, balance sheet, cash flow)
    and calculates key financial ratios and metrics. Also provides trend analysis
    and recommendations based on the financial health of the company.
    
    Args:
        symbol (str): The stock symbol of the company (e.g., 'AAPL')
        
    Returns:
        dict: Financial analysis including metrics, trends, and recommendations
        
    Raises:
        Exception: If there's an error analyzing the data
    """
    logger.info(f"Analyzing financial data for {symbol}")
    try:
        # Create a Ticker object
        stock = yf.Ticker(symbol)
        
        # Get financial statements
        income_stmt = stock.income_stmt
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
        
        # Initialize results dictionary with basic company info
        analysis = {
            "symbol": symbol,
            "company_name": stock.info.get('shortName', 'N/A'),
            "current_price": stock.info.get('currentPrice', 'N/A'),
            "metrics": {},
            "trends": {},
            "recommendations": []
        }
        
        # Calculate key metrics if financial data is available
        if not income_stmt.empty and not balance_sheet.empty:
            try:
                # Get the most recent year's data and previous year for comparison
                latest_year = income_stmt.columns[0]
                prev_year = income_stmt.columns[1] if len(income_stmt.columns) > 1 else None
                
                # Extract key financial figures from statements
                net_income = income_stmt.loc['Net Income', latest_year]
                revenue = income_stmt.loc['Total Revenue', latest_year]
                total_assets = balance_sheet.loc['Total Assets', latest_year]
                total_equity = balance_sheet.loc['Total Stockholder Equity', latest_year]
                
                # Calculate liquidity metrics (handle missing data gracefully)
                current_assets = balance_sheet.loc['Current Assets', latest_year] if 'Current Assets' in balance_sheet.index else None
                current_liabilities = balance_sheet.loc['Current Liabilities', latest_year] if 'Current Liabilities' in balance_sheet.index else None
                
                # Calculate debt metrics (handle missing data gracefully)
                total_debt = balance_sheet.loc['Total Debt', latest_year] if 'Total Debt' in balance_sheet.index else None
                
                # Store calculated metrics in a dictionary
                metrics = {}
                
                # Calculate profitability ratios
                if revenue > 0:
                    metrics["net_profit_margin"] = round((net_income / revenue) * 100, 2)
                
                if total_assets > 0:
                    metrics["return_on_assets"] = round((net_income / total_assets) * 100, 2)
                
                if total_equity > 0:
                    metrics["return_on_equity"] = round((net_income / total_equity) * 100, 2)
                
                # Calculate liquidity ratios
                if current_assets is not None and current_liabilities is not None and current_liabilities > 0:
                    metrics["current_ratio"] = round(current_assets / current_liabilities, 2)
                
                # Calculate solvency ratios
                if total_debt is not None and total_equity > 0:
                    metrics["debt_to_equity"] = round(total_debt / total_equity, 2)
                
                analysis["metrics"] = metrics
                
                # Calculate trends if previous year data is available
                if prev_year is not None:
                    trends = {}
                    
                    # Extract previous year's data for comparison
                    prev_revenue = income_stmt.loc['Total Revenue', prev_year]
                    prev_net_income = income_stmt.loc['Net Income', prev_year]
                    
                    # Calculate year-over-year growth rates
                    if prev_revenue > 0:
                        trends["revenue_growth"] = round(((revenue - prev_revenue) / prev_revenue) * 100, 2)
                    
                    if prev_net_income > 0:
                        trends["net_income_growth"] = round(((net_income - prev_net_income) / prev_net_income) * 100, 2)
                    
                    analysis["trends"] = trends
                
                # Generate recommendations based on financial metrics
                recommendations = []
                
                # ROE recommendations
                if metrics.get("return_on_equity", 0) > 15:
                    recommendations.append("Strong ROE indicates efficient use of shareholder equity")
                elif metrics.get("return_on_equity", 0) < 5:
                    recommendations.append("Low ROE may indicate inefficient use of capital")
                
                # Profit margin recommendations
                if metrics.get("net_profit_margin", 0) > 20:
                    recommendations.append("High profit margin indicates strong pricing power")
                elif metrics.get("net_profit_margin", 0) < 5:
                    recommendations.append("Low profit margin may indicate operational inefficiencies")
                
                # Liquidity recommendations
                if metrics.get("current_ratio", 0) > 2:
                    recommendations.append("Strong liquidity position")
                elif metrics.get("current_ratio", 0) < 1:
                    recommendations.append("Potential liquidity concerns")
                
                # Debt level recommendations
                if metrics.get("debt_to_equity", 0) > 2:
                    recommendations.append("High debt levels may increase financial risk")
                elif metrics.get("debt_to_equity", 0) < 0.5:
                    recommendations.append("Conservative debt levels")
                
                analysis["recommendations"] = recommendations
                
            except Exception as e:
                # Log the error but continue with partial analysis
                logger.error(f"Error calculating financial metrics: {str(e)}")
                analysis["error_details"] = f"Could not calculate some metrics: {str(e)}"
        else:
            analysis["error_details"] = "Insufficient financial data available"
        
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing financial data: {str(e)}")
        raise

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