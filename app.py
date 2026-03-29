from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from math import ceil

import pandas as pd
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key-change-in-production")
app.config["ENV"] = os.getenv("FLASK_ENV", "development")

DATA_PATH = Path(os.getenv("DATA_PATH", "data/vibration_data.csv"))
if not DATA_PATH.is_absolute():
    DATA_PATH = BASE_DIR / DATA_PATH

logger.info(f"Configured data path: {DATA_PATH}")


def classify_point(vibration: float) -> str:
    if vibration >= 0.30:
        return "HIGH RISK"
    if vibration >= 0.22:
        return "EARLY FATIGUE"
    return "SAFE"


def classify_month(avg_vibration: float) -> str:
    if avg_vibration >= 0.30:
        return "CRITICAL"
    if avg_vibration >= 0.22:
        return "EARLY FATIGUE"
    return "NORMAL"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    if "Date" not in df.columns or "Vibration" not in df.columns:
        raise ValueError("Dataset must contain Date and Vibration columns")

    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Vibration"] = pd.to_numeric(df["Vibration"], errors="coerce")
    df = df.dropna(subset=["Date", "Vibration"]).sort_values("Date")
    logger.info(f"Loaded {len(df)} records from {DATA_PATH}")
    return df


def monthly_summary(df: pd.DataFrame) -> list[dict]:
    month_df = (
        df.assign(Month=df["Date"].dt.to_period("M").astype(str))
        .groupby("Month", as_index=False)["Vibration"]
        .mean()
        .rename(columns={"Vibration": "Average Vibration"})
        .sort_values("Month")
    )
    month_df["Status"] = month_df["Average Vibration"].apply(classify_month)
    month_df["Average Vibration"] = month_df["Average Vibration"].map(lambda x: f"{x:.12f}")
    return month_df.to_dict(orient="records")


def paginate_rows(rows: list[dict], page: int, page_size: int) -> tuple[list[dict], dict]:
    total_items = len(rows)
    total_pages = max(1, ceil(total_items / page_size))
    current_page = min(max(page, 1), total_pages)
    start_index = (current_page - 1) * page_size
    end_index = start_index + page_size

    pagination = {
        "current_page": current_page,
        "total_pages": total_pages,
        "page_size": page_size,
        "total_items": total_items,
        "has_previous": current_page > 1,
        "has_next": current_page < total_pages,
        "previous_page": current_page - 1,
        "next_page": current_page + 1,
        "start_item": start_index + 1 if total_items else 0,
        "end_item": min(end_index, total_items),
    }
    return rows[start_index:end_index], pagination


def recent_data(df: pd.DataFrame, limit: int = 10) -> list[dict]:
    recent = df.tail(limit).copy()
    recent["Status"] = recent["Vibration"].apply(classify_point)
    recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d %H:%M:%S")
    recent["Vibration"] = recent["Vibration"].map(lambda x: f"{x:.3f}")
    return recent[["Date", "Vibration", "Status"]].to_dict(orient="records")


def chart_series(df: pd.DataFrame, limit: int = 120) -> tuple[list[str], list[float]]:
    chart_df = df.tail(limit).copy()
    labels = chart_df["Date"].dt.strftime("%Y-%m-%d").tolist()
    values = chart_df["Vibration"].round(3).tolist()
    return labels, values


def get_dataset_stats(df: pd.DataFrame) -> dict:
    """Calculate dataset statistics for dashboard display."""
    safe_count = (df["Vibration"] < 0.22).sum()
    early_fatigue_count = ((df["Vibration"] >= 0.22) & (df["Vibration"] < 0.30)).sum()
    high_risk_count = (df["Vibration"] >= 0.30).sum()

    return {
        "total_records": len(df),
        "date_start": df["Date"].min().strftime("%Y-%m-%d"),
        "date_end": df["Date"].max().strftime("%Y-%m-%d"),
        "safe_count": safe_count,
        "early_fatigue_count": early_fatigue_count,
        "high_risk_count": high_risk_count,
        "vib_min": f"{df['Vibration'].min():.3f}",
        "vib_max": f"{df['Vibration'].max():.3f}",
        "vib_avg": f"{df['Vibration'].mean():.3f}",
    }


@app.route("/", methods=["GET", "POST"])
def index():
    try:
        df = load_data()
        chart_labels, chart_values = chart_series(df)
        dataset_stats = get_dataset_stats(df)
        monthly_page = request.args.get("monthly_page", default=1, type=int)
        monthly_rows, monthly_pagination = paginate_rows(monthly_summary(df), monthly_page, page_size=12)

        analysis_result = None
        selected_date = ""
        input_vibration = ""

        if request.method == "POST":
            selected_date = request.form.get("date", "")
            input_vibration = request.form.get("vibration", "")
            try:
                vibration_val = float(input_vibration)
                analysis_result = {
                    "date": selected_date,
                    "vibration": f"{vibration_val:.3f}",
                    "status": classify_point(vibration_val),
                }
            except ValueError:
                analysis_result = {
                    "date": selected_date,
                    "vibration": input_vibration,
                    "status": "INVALID INPUT",
                }

        return render_template(
            "index.html",
            monthly_rows=monthly_rows,
            monthly_pagination=monthly_pagination,
            recent_rows=recent_data(df),
            chart_labels=chart_labels,
            chart_values=chart_values,
            analysis_result=analysis_result,
            selected_date=selected_date,
            input_vibration=input_vibration,
            stats=dataset_stats,
        )
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template("error.html", error=str(e)), 500


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV") == "development"
    app.run(debug=debug_mode, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

