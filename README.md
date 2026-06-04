# StockPulse AI

## Overview

StockPulse AI is an end-to-end data engineering project that extracts stock market data from the Alpha Vantage REST API, performs data transformation and quality validation, loads data into PostgreSQL, generates machine learning predictions, and prepares datasets for Power BI dashboards.

---

## Technologies

- Python
- PostgreSQL
- Alpha Vantage API
- SQLAlchemy
- Pandas
- Scikit-Learn
- Power BI

---

## Features

- REST API Extraction
- Incremental ETL Loading
- Historical Time-Series Storage
- Data Quality Validation
- Random Forest Prediction Model
- Power BI Analytics

---

## Project Architecture

Alpha Vantage API
→ ETL Pipeline
→ PostgreSQL Warehouse
→ ML Prediction Layer
→ Power BI Dashboard

---

## Installation

pip install -r requirements.txt

---

## Execution

python scripts/stockpulse_pipeline.py

---

## Database Tables

- dim_company
- fact_stock_prices
- stock_predictions
- etl_pipeline_log

---

## Author

Rishabh Gupta