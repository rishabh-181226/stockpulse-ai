import os
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# DATABASE CONNECTION
# ============================================================

load_dotenv()

SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

DATABASE_URI = (
    "postgresql+psycopg2://postgres.wqimjjhddlgjvonmssrd:"
    f"{quote_plus(SUPABASE_DB_PASSWORD)}"
    "@aws-1-us-west-1.pooler.supabase.com:6543/postgres"
)

engine = create_engine(
    DATABASE_URI,
    pool_pre_ping=True,
    pool_recycle=300
)


# ============================================================
# DATA LOADING
# ============================================================

def load_stock_data():
    query = """
    SELECT
        d.stock_symbol,
        d.company_name,
        d.sector,
        f.trading_date,
        f.open_price,
        f.high_price,
        f.low_price,
        f.close_price,
        f.volume,
        f.daily_return_pct,
        f.moving_avg_7,
        f.moving_avg_30,
        f.volatility_score,
        f.rsi_indicator,
        f.macd_indicator
    FROM fact_stock_prices f
    JOIN dim_company d
        ON f.company_id = d.company_id
    ORDER BY d.stock_symbol, f.trading_date;
    """

    df = pd.read_sql(query, engine)
    df["trading_date"] = pd.to_datetime(df["trading_date"])
    return df


def load_outlook_data():
    query = """
    SELECT
        d.stock_symbol,
        d.company_name,
        p.prediction_date,
        p.predicted_close_price,
        p.actual_close_price,
        p.model_name,
        p.model_accuracy,
        p.prediction_timestamp
    FROM stock_predictions p
    JOIN dim_company d
        ON p.company_id = d.company_id
    ORDER BY d.stock_symbol, p.prediction_date;
    """

    try:
        df = pd.read_sql(query, engine)

        if not df.empty:
            df["prediction_date"] = pd.to_datetime(df["prediction_date"])
            df["forecast_gap"] = (
                df["actual_close_price"] - df["predicted_close_price"]
            )
            df["absolute_gap"] = df["forecast_gap"].abs()

        return df

    except Exception:
        return pd.DataFrame()


# ============================================================
# APP SETUP
# ============================================================

app = Dash(__name__)
app.title = "StockPulse Investor Dashboard"

initial_df = load_stock_data()

symbols = sorted(initial_df["stock_symbol"].unique())
min_date = initial_df["trading_date"].min()
max_date = initial_df["trading_date"].max()


# ============================================================
# UI HELPERS
# ============================================================

def make_card(title, value, subtitle):
    return html.Div(
        style={
            "backgroundColor": "white",
            "padding": "22px",
            "borderRadius": "16px",
            "boxShadow": "0 4px 14px rgba(0,0,0,0.08)",
            "textAlign": "center"
        },
        children=[
            html.H4(
                title,
                style={
                    "color": "#6b7280",
                    "marginBottom": "8px",
                    "fontWeight": "600"
                }
            ),
            html.H2(
                value,
                style={
                    "color": "#111827",
                    "margin": "0",
                    "fontWeight": "700"
                }
            ),
            html.P(
                subtitle,
                style={
                    "color": "#6b7280",
                    "fontSize": "13px",
                    "marginTop": "8px"
                }
            )
        ]
    )


def empty_figure(title):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=430
    )
    return fig


# ============================================================
# LAYOUT
# ============================================================

app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f3f6fb",
        "padding": "25px"
    },
    children=[

        html.Div(
            style={
                "backgroundColor": "#111827",
                "padding": "30px",
                "borderRadius": "18px",
                "marginBottom": "25px"
            },
            children=[
                html.H1(
                    "StockPulse Investor Dashboard",
                    style={
                        "textAlign": "center",
                        "color": "white",
                        "marginBottom": "8px"
                    }
                ),
                html.P(
                    "Explore historical stock performance, trend signals, volatility, and short-term price outlooks powered by an automated data pipeline.",
                    style={
                        "textAlign": "center",
                        "fontSize": "17px",
                        "color": "#d1d5db",
                        "maxWidth": "950px",
                        "margin": "auto"
                    }
                )
            ]
        ),

        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "20px",
                "backgroundColor": "white",
                "padding": "22px",
                "borderRadius": "16px",
                "boxShadow": "0 4px 14px rgba(0,0,0,0.08)"
            },
            children=[

                html.Div([
                    html.Label(
                        "Choose a Stock",
                        style={"fontWeight": "600", "color": "#374151"}
                    ),
                    dcc.Dropdown(
                        id="stock-dropdown",
                        options=[
                            {"label": symbol, "value": symbol}
                            for symbol in symbols
                        ],
                        value=symbols[0],
                        clearable=False
                    )
                ]),

                html.Div([
                    html.Label(
                        "Analyze Date Range",
                        style={"fontWeight": "600", "color": "#374151"}
                    ),
                    dcc.DatePickerRange(
                        id="date-range",
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        start_date=min_date,
                        end_date=max_date,
                        display_format="YYYY-MM-DD"
                    )
                ])
            ]
        ),

        dcc.Interval(
            id="refresh-interval",
            interval=60 * 1000,
            n_intervals=0
        ),

        html.H2(
            "Market Snapshot",
            style={
                "marginTop": "32px",
                "color": "#111827"
            }
        ),

        html.Div(
            id="market-kpi-cards",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "16px",
                "marginBottom": "25px"
            }
        ),

        dcc.Graph(id="price-chart"),

        html.H2(
            "Price Outlook & Performance Check",
            style={
                "marginTop": "35px",
                "color": "#111827"
            }
        ),

        html.P(
            "This section compares the system-generated short-term price outlook with observed market results to show how closely recent estimates align with actual movement.",
            style={
                "color": "#4b5563",
                "fontSize": "15px",
                "marginTop": "-8px"
            }
        ),

        html.Div(
            id="outlook-kpi-cards",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "16px",
                "marginBottom": "25px"
            }
        ),

        dcc.Graph(id="outlook-chart"),
        dcc.Graph(id="forecast-gap-chart"),

        html.H2(
            "Trend & Risk Signals",
            style={
                "marginTop": "35px",
                "color": "#111827"
            }
        ),

        dcc.Graph(id="moving-average-chart"),
        dcc.Graph(id="technical-indicators-chart"),
        dcc.Graph(id="volume-chart"),
        dcc.Graph(id="candlestick-chart")
    ]
)


# ============================================================
# CALLBACK
# ============================================================

@app.callback(
    [
        Output("market-kpi-cards", "children"),
        Output("outlook-kpi-cards", "children"),
        Output("price-chart", "figure"),
        Output("outlook-chart", "figure"),
        Output("forecast-gap-chart", "figure"),
        Output("moving-average-chart", "figure"),
        Output("technical-indicators-chart", "figure"),
        Output("volume-chart", "figure"),
        Output("candlestick-chart", "figure")
    ],
    [
        Input("stock-dropdown", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("refresh-interval", "n_intervals")
    ]
)
def update_dashboard(selected_stock, start_date, end_date, n_intervals):

    stock_df = load_stock_data()
    outlook_df = load_outlook_data()

    filtered = stock_df[
        (stock_df["stock_symbol"] == selected_stock)
        & (stock_df["trading_date"] >= pd.to_datetime(start_date))
        & (stock_df["trading_date"] <= pd.to_datetime(end_date))
    ].sort_values("trading_date")

    if filtered.empty:
        return (
            [],
            [],
            empty_figure("No stock data available"),
            empty_figure("No outlook data available"),
            empty_figure("No forecast gap data available"),
            empty_figure("No moving average data available"),
            empty_figure("No indicator data available"),
            empty_figure("No volume data available"),
            empty_figure("No candlestick data available")
        )

    filtered_outlook = (
        outlook_df[outlook_df["stock_symbol"] == selected_stock]
        .sort_values("prediction_date")
        if not outlook_df.empty
        else pd.DataFrame()
    )

    latest = filtered.iloc[-1]

    market_cards = [
        make_card(
            "Latest Close",
            f"${round(latest['close_price'], 2)}",
            "Most recent closing price"
        ),
        make_card(
            "Volume",
            f"{int(latest['volume']):,}",
            "Latest trading activity"
        ),
        make_card(
            "Daily Move",
            f"{round(latest['daily_return_pct'], 2)}%",
            "Close price compared with open"
        ),
        make_card(
            "Volatility",
            f"{round(latest['volatility_score'], 2)}",
            "Daily high minus daily low"
        )
    ]

    if not filtered_outlook.empty:

        latest_outlook = filtered_outlook.iloc[-1]

        projected_close = round(latest_outlook["predicted_close_price"], 2)
        observed_close = round(latest_outlook["actual_close_price"], 2)
        forecast_gap = round(latest_outlook["forecast_gap"], 2)
        reliability = round(latest_outlook["model_accuracy"], 4)

        outlook_cards = [
            make_card(
                "Projected Close",
                f"${projected_close}",
                "Short-term price outlook"
            ),
            make_card(
                "Observed Close",
                f"${observed_close}",
                "Actual market result"
            ),
            make_card(
                "Forecast Gap",
                f"${forecast_gap}",
                "Observed minus projected"
            ),
            make_card(
                "Reliability Score",
                f"{reliability}",
                "Model fit indicator"
            )
        ]

    else:

        outlook_cards = [
            make_card("Projected Close", "N/A", "No outlook data available"),
            make_card("Observed Close", "N/A", "No outlook data available"),
            make_card("Forecast Gap", "N/A", "No outlook data available"),
            make_card("Reliability Score", "N/A", "No outlook data available")
        ]

    price_fig = px.line(
        filtered,
        x="trading_date",
        y="close_price",
        title=f"{selected_stock} Historical Closing Price",
        labels={
            "trading_date": "Date",
            "close_price": "Closing Price"
        }
    )

    if not filtered_outlook.empty:

        outlook_fig = go.Figure()

        outlook_fig.add_trace(
            go.Scatter(
                x=filtered_outlook["prediction_date"],
                y=filtered_outlook["predicted_close_price"],
                mode="lines+markers",
                name="Projected Close"
            )
        )

        outlook_fig.add_trace(
            go.Scatter(
                x=filtered_outlook["prediction_date"],
                y=filtered_outlook["actual_close_price"],
                mode="lines+markers",
                name="Observed Close"
            )
        )

        outlook_fig.update_layout(
            title=f"{selected_stock} Projected vs Observed Price Movement",
            xaxis_title="Date",
            yaxis_title="Close Price"
        )

        gap_fig = px.bar(
            filtered_outlook,
            x="prediction_date",
            y="forecast_gap",
            title=f"{selected_stock} Forecast Gap Over Time",
            labels={
                "prediction_date": "Date",
                "forecast_gap": "Forecast Gap"
            }
        )

    else:

        outlook_fig = empty_figure("No Price Outlook Data Available")
        gap_fig = empty_figure("No Forecast Gap Data Available")

    ma_fig = go.Figure()

    ma_fig.add_trace(
        go.Scatter(
            x=filtered["trading_date"],
            y=filtered["close_price"],
            mode="lines",
            name="Close Price"
        )
    )

    ma_fig.add_trace(
        go.Scatter(
            x=filtered["trading_date"],
            y=filtered["moving_avg_7"],
            mode="lines",
            name="7-Day Trend"
        )
    )

    ma_fig.add_trace(
        go.Scatter(
            x=filtered["trading_date"],
            y=filtered["moving_avg_30"],
            mode="lines",
            name="30-Day Trend"
        )
    )

    ma_fig.update_layout(
        title=f"{selected_stock} Short-Term vs Long-Term Trend",
        xaxis_title="Date",
        yaxis_title="Price"
    )

    technical_fig = go.Figure()

    technical_fig.add_trace(
        go.Scatter(
            x=filtered["trading_date"],
            y=filtered["rsi_indicator"],
            mode="lines",
            name="RSI"
        )
    )

    technical_fig.add_trace(
        go.Scatter(
            x=filtered["trading_date"],
            y=filtered["macd_indicator"],
            mode="lines",
            name="MACD"
        )
    )

    technical_fig.update_layout(
        title=f"{selected_stock} Momentum Indicators",
        xaxis_title="Date",
        yaxis_title="Indicator Value"
    )

    volume_fig = px.bar(
        filtered,
        x="trading_date",
        y="volume",
        title=f"{selected_stock} Trading Volume Pattern",
        labels={
            "trading_date": "Date",
            "volume": "Volume"
        }
    )

    candlestick_fig = go.Figure(
        data=[
            go.Candlestick(
                x=filtered["trading_date"],
                open=filtered["open_price"],
                high=filtered["high_price"],
                low=filtered["low_price"],
                close=filtered["close_price"],
                name=selected_stock
            )
        ]
    )

    candlestick_fig.update_layout(
        title=f"{selected_stock} Daily Price Range",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False
    )

    for fig in [
        price_fig,
        outlook_fig,
        gap_fig,
        ma_fig,
        technical_fig,
        volume_fig,
        candlestick_fig
    ]:
        fig.update_layout(
            template="plotly_white",
            height=440,
            margin=dict(l=40, r=40, t=60, b=40)
        )

    return (
        market_cards,
        outlook_cards,
        price_fig,
        outlook_fig,
        gap_fig,
        ma_fig,
        technical_fig,
        volume_fig,
        candlestick_fig
    )


# ============================================================
# RUN APP
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)