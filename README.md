# StockPulse AI

## Overview

StockPulse AI is an end-to-end data engineering and analytics platform that extracts stock market data from the Alpha Vantage API, performs transformation and data quality validation, stores historical data in a PostgreSQL warehouse hosted on Supabase, generates short-term price outlooks using machine learning, and presents insights through an interactive Dash dashboard.

The project demonstrates modern data engineering concepts including ETL automation, incremental loading, feature engineering, machine learning integration, and interactive analytics.

---

# Technologies

### Data Engineering

* Python
* PostgreSQL (Supabase)
* SQLAlchemy
* Pandas
* NumPy

### Data Source

* Alpha Vantage REST API

### Machine Learning

* Scikit-Learn
* Random Forest Regressor
* Joblib

### Visualization

* Dash
* Plotly

### Development Tools

* VS Code
* Git
* GitHub

---

# Features

### Data Pipeline

* API-based stock data extraction
* Incremental ETL loading strategy
* Historical time-series storage
* Data cleaning and validation
* Logging and error handling

### Feature Engineering

* Daily return percentage
* 7-Day moving average
* 30-Day moving average
* Volatility score
* RSI indicator
* MACD indicator

### Machine Learning

* Random Forest Regression model
* Short-term price prediction
* Prediction performance evaluation
* Prediction history storage

### Interactive Analytics

* Historical stock performance tracking
* Trend analysis
* Technical indicators
* Trading volume analysis
* Candlestick charts
* Price outlook analysis

---

# Project Architecture

```
Alpha Vantage API
        ↓
Python ETL Pipeline
        ↓
Data Cleaning & Validation
        ↓
Supabase PostgreSQL Data Warehouse
        ↓
Feature Engineering
        ↓
Random Forest Prediction Model
        ↓
Dash Interactive Analytics Dashboard
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/rishabh-181226/stockpulse-ai.git
```

Navigate to the project directory:

```bash
cd stockpulse-ai
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the ETL Pipeline

Navigate to the scripts directory:

```bash
cd scripts
```

Run the pipeline:

```bash
python stockpulse_pipeline.py
```

The pipeline performs:

* Data extraction from Alpha Vantage
* Transformation and cleaning
* Data quality validation
* Incremental loading into PostgreSQL
* Feature engineering
* Machine learning model training
* Prediction generation

---

# Running the Dashboard

Navigate to the dashboard directory:

```bash
cd dashboard
```

Run the application:

```bash
python app.py
```

Open the dashboard:

```
http://127.0.0.1:8050
```

---

# Database Tables

## dim_company

Stores company metadata.

| Column       |
| ------------ |
| company_id   |
| stock_symbol |
| company_name |
| sector       |

---

## fact_stock_prices

Stores historical stock market observations and engineered features.

| Column           |
| ---------------- |
| company_id       |
| trading_date     |
| open_price       |
| high_price       |
| low_price        |
| close_price      |
| adjusted_close   |
| volume           |
| daily_return_pct |
| moving_avg_7     |
| moving_avg_30    |
| volatility_score |
| rsi_indicator    |
| macd_indicator   |

---

## stock_predictions

Stores prediction outputs and model metrics.

| Column                |
| --------------------- |
| company_id            |
| prediction_date       |
| predicted_close_price |
| actual_close_price    |
| model_name            |
| model_accuracy        |
| prediction_timestamp  |

---

## etl_pipeline_log

Stores ETL execution history.

| Column            |
| ----------------- |
| job_name          |
| records_processed |
| pipeline_status   |
| error_message     |

---

# Dashboard Features

### Market Snapshot

* Latest Close Price
* Trading Volume
* Daily Return
* Volatility Score

### Price Outlook & Performance Check

* Projected Close Price
* Observed Close Price
* Forecast Gap
* Reliability Score

### Visualizations

* Historical Price Trend
* Projected vs Observed Price Movement
* Forecast Gap Analysis
* Moving Average Trend Analysis
* RSI Indicator
* MACD Indicator
* Trading Volume Analysis
* Candlestick Chart

---

# Machine Learning Model

### Model

Random Forest Regressor

### Features

* Volume
* Daily Return Percentage
* Moving Average (7-day)
* Moving Average (30-day)
* Volatility Score
* RSI Indicator
* MACD Indicator

### Target Variable

Next-Day Closing Price

### Evaluation Metrics

* Mean Absolute Error (MAE)
* Root Mean Squared Error (RMSE)
* R² Score

---

# Repository Structure

```
stockpulse-ai/
│
├── dashboard/
│   ├── app.py
│   └── README.md
│
├── scripts/
│   └── stockpulse_pipeline.py
│
├── requirements.txt
├── README.md
├── .gitignore
└── screenshots/
```

---

# Author

**Rishabh Gupta**
