# StockPulse Investor Dashboard

## Overview

The StockPulse Investor Dashboard is an interactive analytics application built with Dash and Plotly. The dashboard connects directly to the PostgreSQL database and provides users with access to historical stock performance, trend indicators, volatility metrics, and short-term price outlook analysis.

The application allows users to dynamically explore market behavior and compare projected price movement with observed market results through an intuitive and interactive interface.

---

# How to Run the Dash Application

## 1. Activate the Virtual Environment

From the project root directory:

```bash
.\venv\Scripts\activate
```

## 2. Navigate to the Dashboard Folder

```bash
cd dashboard
```

## 3. Run the Application

```bash
python app.py
```

## 4. Open the Dashboard

Open your browser and visit:

```text
http://127.0.0.1:8050
```

---

# Dependencies

Install dependencies from the project root directory:

```bash
pip install -r requirements.txt
```

Main libraries used:

* Dash
* Plotly
* Pandas
* SQLAlchemy
* psycopg2-binary
* python-dotenv

---

# Dashboard Components

## Interactive Filters

The dashboard provides interactive controls that allow users to explore the data dynamically.

### Stock Symbol Dropdown

Users can select among:

* AAPL
* MSFT
* TSLA
* NVDA
* AMZN

### Date Range Filter

Users can choose a custom date range to analyze historical performance.

### Automatic Refresh

The dashboard refreshes automatically and updates visualizations without requiring a restart.

---

# KPI Cards

## Market Snapshot

The dashboard provides summary metrics including:

* Latest Close Price
* Trading Volume
* Daily Return
* Volatility Score

## Price Outlook & Performance Check

The dashboard displays:

* Projected Close Price
* Observed Close Price
* Forecast Gap
* Reliability Score

---

# Visualizations

## Historical Price Trend

Displays stock closing price movement over time and helps identify long-term trends.

---

## Projected vs Observed Price Movement

Compares projected price values with observed market results to evaluate short-term price outlooks.

---

## Forecast Gap Analysis

Shows the difference between projected and observed prices over time.

---

## Trend Analysis

Displays:

* Closing Price
* 7-Day Moving Average
* 30-Day Moving Average

These metrics help identify short-term and long-term market trends.

---

## Technical Indicator Analysis

Visualizes:

* RSI (Relative Strength Index)
* MACD (Moving Average Convergence Divergence)

These indicators provide insight into momentum and market conditions.

---

## Trading Volume Analysis

Shows changes in trading activity across time.

---

## Candlestick Chart

Displays:

* Open Price
* High Price
* Low Price
* Close Price

This visualization provides detailed insight into daily price movements.

---

# Business Insights

## Historical Performance Monitoring

Users can analyze historical stock behavior and observe how prices evolve over time.

---

## Trend Detection

Moving averages help identify short-term and long-term trends and provide insight into market direction.

---

## Momentum Analysis

RSI and MACD indicators help users understand whether stocks are experiencing stronger or weaker momentum.

---

## Volatility Assessment

Daily price ranges help identify periods of increased market uncertainty and risk.

---

## Price Outlook Evaluation

The dashboard compares projected prices with observed market performance to assess how closely recent estimates align with actual market movement.

---

## Forecast Gap Analysis

Users can monitor differences between projected and observed prices to better understand forecasting performance.

---

# User Experience Features

The application provides:

* Interactive filtering
* Dynamic chart updates
* Professional dashboard layout
* Clear titles and labels
* Responsive visualizations
* Multiple analytical views
* Automatic refresh capability

---


# Key Dashboard Features Summary

✅ PostgreSQL database integration

✅ Interactive Dash application

✅ Multiple visualizations

✅ Dynamic filtering

✅ KPI cards

✅ Historical performance analysis

✅ Trend analysis

✅ Technical indicators

✅ Price outlook analysis

✅ Professional and intuitive user interface
