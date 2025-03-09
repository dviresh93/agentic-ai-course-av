# Yahoo Finance API

A Flask-based API for retrieving and analyzing stock market data from Yahoo Finance.

## Project Overview

This application provides a comprehensive interface for accessing financial data through a set of robust API endpoints. It allows users to retrieve company information, historical price data, news, and perform advanced financial analysis through both a web interface and programmatic API access.

## Features

- **Company Information**: Retrieve detailed company profiles, sector, industry, and key metrics
- **Historical Price Data**: Access historical stock prices with customizable date ranges
- **News Aggregation**: Get the latest news articles related to specific companies
- **Technical Analysis**: Analyze historical data for trends, patterns, and insights
- **Financial Statement Analysis**: Examine company financials and performance metrics
- **Interactive Web Interface**: User-friendly forms for data exploration
- **RESTful API**: Programmatic access to all data endpoints

## Project Structure
- `app/`: Application package
  - `__init__.py`: Application factory
  - `routes.py`: API endpoints
  - `services.py`: Business logic
  - `errors.py`: Error handling
  - `templates/`: HTML templates
- `config.py`: Configuration settings
- `run.py`: Application entry point
- `cert.pem` & `key.pem`: SSL certificates (optional)

## Implementation Details

### Core Components

1. **Data Retrieval Layer** (`services.py`)
   - Interfaces with Yahoo Finance API through the yfinance library
   - Handles data fetching, parsing, and formatting
   - Implements error handling and retry logic

2. **Analysis Engine** (`services.py`)
   - Performs technical analysis on historical price data
   - Calculates key financial ratios and metrics
   - Generates insights and recommendations based on data patterns

3. **API Layer** (`routes.py`)
   - Defines RESTful endpoints with proper HTTP methods
   - Validates input parameters and handles errors
   - Returns well-structured JSON responses

4. **Web Interface** (`templates/`)
   - Provides user-friendly forms for data exploration
   - Displays results in formatted tables and charts
   - Implements responsive design for various devices

### API Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/` | GET | Homepage with interactive forms | None |
| `/company` | GET | Company information | `symbol` (required) |
| `/historical` | GET/POST | Historical price data | `symbol`, `start_date`, `end_date` (all required) |
| `/news` | GET | Company news articles | `symbol` (required) |
| `/analyze-financials` | GET | Financial statement analysis | `symbol` (required) |
| `/analyze-historical` | POST | Technical analysis of price data | `symbol`, `start_date`, `end_date` (all required) |

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python run.py`

## API Endpoints
- GET `/`: Homepage with forms
- GET `/company?symbol=SYMBOL`: Get company information
- GET/POST `/historical`: Get historical price data
- GET `/news?symbol=SYMBOL`: Get company news
- GET `/financials?symbol=SYMBOL`: Get financial data
- POST `/analyze-historical`: Analyze historical data

## Usage Examples

### Web Interface

1. Navigate to http://localhost:5000
2. Select the desired data type (Company Info, Historical Data, etc.)
3. Enter the company symbol (e.g., "AAPL" for Apple)
4. For historical data, specify the date range
5. Click the corresponding button to retrieve data

