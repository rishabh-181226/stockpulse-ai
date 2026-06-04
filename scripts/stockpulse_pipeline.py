# ============================================================
# STOCKPULSE AI
# COMPLETE END-TO-END DATA ENGINEERING PIPELINE
# WITH:
# ✔ API EXTRACTION
# ✔ DATA QUALITY ENGINEERING
# ✔ POSTGRESQL LOADING
# ✔ MACHINE LEARNING PREDICTION
# ✔ POWER BI READY OUTPUT
# ============================================================

# ============================================================
# IMPORT LIBRARIES
# ============================================================
print("Script started")
import os
import logging
import requests
import pandas as pd
import numpy as np
import time

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy import text

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

import joblib


# ============================================================
# LOAD ENVIRONMENT VARIABLES + SUPABASE CONNECTION
# ============================================================

from urllib.parse import quote_plus

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

if not SUPABASE_DB_PASSWORD:
    raise ValueError("SUPABASE_DB_PASSWORD missing in .env")

SUPABASE_DB_PASSWORD = quote_plus(SUPABASE_DB_PASSWORD)

DATABASE_URI = (
    "postgresql+psycopg2://postgres.wqimjjhddlgjvonmssrd:"
    f"{SUPABASE_DB_PASSWORD}"
    "@aws-1-us-west-1.pooler.supabase.com:6543/postgres"
)

print("DATABASE URI LOADED")
print("HOST: aws-1-us-west-1.pooler.supabase.com")

engine = create_engine(
    DATABASE_URI,
    pool_pre_ping=True,
    pool_recycle=300
)
# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s - %(levelname)s - %(message)s",

    handlers=[

        logging.FileHandler("etl_pipeline.log"),

        logging.StreamHandler()
    ]
)
def test_database_connection():

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("SELECT NOW();")
            )

            logging.info(
                f"Supabase connection successful: {result.fetchone()[0]}"
            )

    except Exception as e:

        logging.error(
            f"Database connection failed: {e}"
        )

        raise
# ============================================================
# API CONFIGURATION
# ============================================================

BASE_URL = "https://www.alphavantage.co/query"

TRACKED_STOCKS = [

    "AAPL",
    "MSFT",
    "TSLA",
    "NVDA",
    "AMZN"
]

# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def create_tables():

    logging.info("Creating PostgreSQL tables")

    with engine.connect() as conn:

        # ----------------------------------------------------
        # DIMENSION TABLE
        # ----------------------------------------------------

        conn.execute(text("""

        CREATE TABLE IF NOT EXISTS dim_company (

            company_id SERIAL PRIMARY KEY,

            stock_symbol VARCHAR(10) UNIQUE NOT NULL,

            company_name VARCHAR(100),

            sector VARCHAR(100),

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        """))

        # ----------------------------------------------------
        # FACT TABLE
        # ----------------------------------------------------

        conn.execute(text("""

        CREATE TABLE IF NOT EXISTS fact_stock_prices (

            stock_price_id BIGSERIAL PRIMARY KEY,

            company_id INTEGER REFERENCES dim_company(company_id),

            trading_date DATE NOT NULL,

            open_price NUMERIC(12,2),

            high_price NUMERIC(12,2),

            low_price NUMERIC(12,2),

            close_price NUMERIC(12,2),

            adjusted_close NUMERIC(12,2),

            volume BIGINT,

            daily_return_pct NUMERIC(10,4),

            moving_avg_7 NUMERIC(12,2),

            moving_avg_30 NUMERIC(12,2),

            volatility_score NUMERIC(12,4),

            rsi_indicator NUMERIC(10,4),

            macd_indicator NUMERIC(10,4),

            etl_load_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        
            CONSTRAINT unique_stock_day
            
            UNIQUE(company_id, trading_date)
        );

        """))

        # ----------------------------------------------------
        # PREDICTION TABLE
        # ----------------------------------------------------

        conn.execute(text("""

        CREATE TABLE IF NOT EXISTS stock_predictions (

            prediction_id BIGSERIAL PRIMARY KEY,

            company_id INTEGER REFERENCES dim_company(company_id),

            prediction_date DATE,

            predicted_close_price NUMERIC(12,2),

            actual_close_price NUMERIC(12,2),

            model_name VARCHAR(100),

            model_accuracy NUMERIC(10,4),

            prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        """))

        # ----------------------------------------------------
        # ETL LOG TABLE
        # ----------------------------------------------------

        conn.execute(text("""

        CREATE TABLE IF NOT EXISTS etl_pipeline_log (

            job_id SERIAL PRIMARY KEY,

            job_name VARCHAR(100),

            execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            records_processed INTEGER,

            pipeline_status VARCHAR(20),

            error_message TEXT
        );

        """))

        conn.commit()

# ============================================================
# LOAD COMPANY DIMENSION
# ============================================================

def load_company_dimension():

    company_df = pd.DataFrame([

        {
            "stock_symbol": "AAPL",
            "company_name": "Apple",
            "sector": "Technology"
        },

        {
            "stock_symbol": "MSFT",
            "company_name": "Microsoft",
            "sector": "Technology"
        },

        {
            "stock_symbol": "TSLA",
            "company_name": "Tesla",
            "sector": "Automotive"
        },

        {
            "stock_symbol": "NVDA",
            "company_name": "NVIDIA",
            "sector": "Semiconductors"
        },

        {
            "stock_symbol": "AMZN",
            "company_name": "Amazon",
            "sector": "E-Commerce"
        }

    ])

    existing = pd.read_sql(

        "SELECT stock_symbol FROM dim_company",

        engine
    )

    new_companies = company_df[
        ~company_df["stock_symbol"]
        .isin(existing["stock_symbol"])
    ]

    if len(new_companies) > 0:

        new_companies.to_sql(

            "dim_company",

            engine,

            if_exists="append",

            index=False
        )

# ============================================================
# API EXTRACTION
# ============================================================

# ============================================================
# ============================================================
# API EXTRACTION WITH RETRY LOGIC
# ============================================================

def extract_stock_data(symbol):

    logging.info(f"Extracting data for {symbol}")

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY,
        "outputsize": "compact"
    }

    max_retries = 3

    for attempt in range(max_retries):

        try:

            response = requests.get(
                BASE_URL,
                params=params,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            print(f"\nAlpha Vantage response keys for {symbol}: {list(data.keys())}\n")

            if "Note" in data:
                logging.warning(
                    "Alpha Vantage rate limit reached. Waiting 60 seconds..."
                )
                time.sleep(60)
                continue

            if "Information" in data:
                raise Exception(
                    f"Alpha Vantage returned information message: {data['Information']}"
                )

            if "Error Message" in data:
                raise Exception(
                    f"API Error: {data['Error Message']}"
                )

            if "Time Series (Daily)" not in data:
                raise Exception(
                    f"Time Series data not found. Response keys: {list(data.keys())}"
                )

            logging.info(f"Successfully extracted {symbol}")

            return data

        except Exception as e:

            logging.warning(
                f"{symbol} attempt {attempt + 1} failed: {e}"
            )

            if attempt < max_retries - 1:
                logging.info("Retrying in 5 seconds...")
                time.sleep(5)

    raise Exception(
        f"Failed to retrieve stock data for {symbol} after {max_retries} attempts"
    )

# ============================================================
# RSI CALCULATION
# ============================================================

def calculate_rsi(data, window=14):

    delta = data.diff()

    gain = (
        delta.where(delta > 0, 0)
        .rolling(window=window)
        .mean()
    )

    loss = (
        -delta.where(delta < 0, 0)
        .rolling(window=window)
        .mean()
    )

    rs = gain / loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

# ============================================================
# MACD CALCULATION
# ============================================================

def calculate_macd(data):

    ema_12 = data.ewm(span=12).mean()

    ema_26 = data.ewm(span=26).mean()

    macd = ema_12 - ema_26

    return macd

# ============================================================
# TRANSFORMATION LAYER
# ============================================================

def transform_stock_data(symbol, raw_data):

    logging.info(f"Transforming data for {symbol}")

    if "Time Series (Daily)" not in raw_data:
        logging.error("Invalid API response")
        return pd.DataFrame()

    df = pd.DataFrame(
        raw_data["Time Series (Daily)"]
    ).T

    df.reset_index(inplace=True)

    # TIME_SERIES_DAILY returns:
    # date, open, high, low, close, volume
    df.columns = [
        "trading_date",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume"
    ]

    # Since this endpoint does not provide adjusted close,
    # we use close_price as adjusted_close for schema compatibility.
    df["adjusted_close"] = df["close_price"]

    numeric_columns = [
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "adjusted_close",
        "volume"
    ]

    df[numeric_columns] = (
        df[numeric_columns]
        .astype(float)
    )

    df["trading_date"] = pd.to_datetime(
        df["trading_date"]
    )

    df["stock_symbol"] = symbol

    df = df.dropna()
    df = df.drop_duplicates()

    df["daily_return_pct"] = (
        (
            df["close_price"]
            - df["open_price"]
        )
        / df["open_price"]
    ) * 100

    df["moving_avg_7"] = (
        df["close_price"]
        .rolling(window=7)
        .mean()
    )

    df["moving_avg_30"] = (
        df["close_price"]
        .rolling(window=30)
        .mean()
    )

    df["volatility_score"] = (
        df["high_price"]
        - df["low_price"]
    )

    df["rsi_indicator"] = calculate_rsi(
        df["close_price"]
    )

    df["macd_indicator"] = calculate_macd(
        df["close_price"]
    )

    return df

    # --------------------------------------------------------
    # FEATURE ENGINEERING
    # --------------------------------------------------------

    df["daily_return_pct"] = (

        (
            df["close_price"]
            - df["open_price"]
        )

        / df["open_price"]

    ) * 100

    df["moving_avg_7"] = (

        df["close_price"]

        .rolling(window=7)

        .mean()
    )

    df["moving_avg_30"] = (

        df["close_price"]

        .rolling(window=30)

        .mean()
    )

    df["volatility_score"] = (

        df["high_price"]

        - df["low_price"]
    )

    df["rsi_indicator"] = calculate_rsi(
        df["close_price"]
    )

    df["macd_indicator"] = calculate_macd(
        df["close_price"]
    )

    return df

# ============================================================
# DATA VALIDATION
# ============================================================

def validate_data(df):

    logging.info("Running validation checks")

    if df.isnull().sum().sum() > 0:

        logging.warning("Null values detected")

    else:

        logging.info("Null validation passed")

    duplicate_count = df.duplicated().sum()

    if duplicate_count > 0:

        logging.warning(
            f"Duplicate rows detected: {duplicate_count}"
        )

    else:

        logging.info("Duplicate validation passed")

    if (df["close_price"] < 0).any():

        logging.error("Negative stock price detected")

    else:

        logging.info("Price range validation passed")

# ============================================================
# INCREMENTAL LOADING
# ============================================================

def incremental_load(df):

    logging.info("Performing incremental load")

    existing_data = pd.read_sql("""

    SELECT company_id, trading_date
    FROM fact_stock_prices

    """, engine)
    
    if not existing_data.empty:

        existing_data["trading_date"] = (
            pd.to_datetime(
                existing_data["trading_date"]
            ).dt.date
        )

    company_lookup = pd.read_sql(

        "SELECT * FROM dim_company",

        engine
    )

    merged_df = df.merge(

        company_lookup,

        on="stock_symbol",

        how="left"
    )

    fact_df = merged_df[[

        "company_id",
        "trading_date",
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "adjusted_close",
        "volume",
        "daily_return_pct",
        "moving_avg_7",
        "moving_avg_30",
        "volatility_score",
        "rsi_indicator",
        "macd_indicator"
    ]].copy()

    fact_df["trading_date"] = (
        pd.to_datetime(
            fact_df["trading_date"]
        ).dt.date
    )

    
    print("FACT TYPE:", fact_df["trading_date"].dtype)

    print("EXISTING TYPE:", existing_data["trading_date"].dtype)
    
    merged_existing = fact_df.merge(
        existing_data,
        on=["company_id", "trading_date"],
        how="left",
        indicator=True
    )


    new_records = merged_existing[
        merged_existing["_merge"] == "left_only"
    ]

    new_records = new_records.drop(
        columns=["_merge"]
    )

    if len(new_records) > 0:

        new_records.to_sql(

            "fact_stock_prices",

            engine,

            if_exists="append",

            index=False
        )

        logging.info(
            f"{len(new_records)} new records inserted"
        )

    else:

        logging.info("No new records found")

# ============================================================
# MACHINE LEARNING PREDICTION
# ============================================================

def train_prediction_model():

    logging.info("Starting ML model training")

    query = """

    SELECT
        company_id,
        trading_date,
        close_price,
        volume,
        daily_return_pct,
        moving_avg_7,
        moving_avg_30,
        volatility_score,
        rsi_indicator,
        macd_indicator
    FROM fact_stock_prices

    """

    df = pd.read_sql(query, engine)

    df = df.sort_values(
        by=["company_id", "trading_date"]
    )

    df["target_close_price"] = (
        df.groupby("company_id")["close_price"]
        .shift(-1)
    )

    df = df.dropna()

    X = df[[
        "volume",
        "daily_return_pct",
        "moving_avg_7",
        "moving_avg_30",
        "volatility_score",
        "rsi_indicator",
        "macd_indicator"
    ]]

    y = df["target_close_price"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=120226
    )

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=120226
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)

    rmse = np.sqrt(
        mean_squared_error(y_test, predictions)
    )

    r2 = r2_score(y_test, predictions)

    logging.info(f"MAE: {mae}")
    logging.info(f"RMSE: {rmse}")
    logging.info(f"R2 Score: {r2}")

    joblib.dump(
        model,
        "stock_prediction_model.pkl"
    )

    logging.info("Model saved successfully")

    prediction_df = pd.DataFrame({

        "company_id": df.loc[X_test.index, "company_id"].values,

        "prediction_date": df.loc[X_test.index, "trading_date"].values,

        "predicted_close_price": predictions,

        "actual_close_price": y_test.values,

        "model_name": "RandomForestRegressor",

        "model_accuracy": r2
    })

    prediction_df = prediction_df.drop_duplicates()

    try:

        prediction_df.to_sql(
            "stock_predictions",
            engine,
            if_exists="append",
            index=False
        )

        logging.info("Predictions saved successfully")

    except Exception as e:

        logging.warning(
            f"Error occurred while saving predictions: {e}"
        )
        
 
# ============================================================
# PIPELINE EXECUTION LOGGING
# ============================================================

def log_pipeline_execution(

    total_records,

    status,

    error_message=None
):

    log_df = pd.DataFrame([{

        "job_name": "StockPulse AI Pipeline",

        "records_processed": total_records,

        "pipeline_status": status,

        "error_message": error_message
    }])

    log_df.to_sql(

        "etl_pipeline_log",

        engine,

        if_exists="append",

        index=False
    )

# ============================================================
# MAIN PIPELINE
# ============================================================

def run_pipeline():

    try:

        logging.info("Starting ETL pipeline")
        
        test_database_connection()

        create_tables()

        load_company_dimension()

        total_records = 0

        for stock in TRACKED_STOCKS:

            logging.info(f"Processing {stock}")
            
            raw_data = extract_stock_data(stock)

            transformed_df = transform_stock_data(

                stock,

                raw_data
            )

            validate_data(transformed_df)

            incremental_load(transformed_df)

            total_records += len(transformed_df)
            
            logging.info(
                "Waiting 12 seconds to avoid Alpha Vantage rate limit..."
            )
            
            time.sleep(12)

        # ----------------------------------------------------
        # ML TRAINING
        # ----------------------------------------------------

        train_prediction_model()

        # ----------------------------------------------------
        # PIPELINE LOGGING
        # ----------------------------------------------------

        log_pipeline_execution(

            total_records=total_records,

            status="SUCCESS"
        )

        logging.info(
            "Complete pipeline executed successfully"
        )

    except Exception as e:

        logging.error(f"Pipeline failed: {str(e)}")

        log_pipeline_execution(

            total_records=0,

            status="FAILED",

            error_message=str(e)
        )

# ============================================================
# EXECUTE PIPELINE
# ============================================================

if __name__ == "__main__":

    run_pipeline()