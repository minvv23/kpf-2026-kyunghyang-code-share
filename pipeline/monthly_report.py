"""월간 리포트 집계 (달력 월 기준)."""
import calendar

import pandas as pd

from . import config, storage
from .build_dataset import load_dataset
from .utils.logging_utils import get_logger

log = get_logger(__name__)


def month_dates(month: str):
    y, m = int(month[:4]), int(month[4:6])
    last = calendar.monthrange(y, m)[1]
    return [f"{month}{d:02d}" for d in range(1, last + 1)]


def kpi(df: pd.DataFrame) -> dict:
    return {
        "n_articles": int(len(df)),
        "total_pv": int(df["pv"].sum()),
        "mean_pv": round(float(df["pv"].mean()), 1),
        "median_pv": float(df["pv"].median()),
        "median_stay_sec": float(df["stay_sec"].median()) if "stay_sec" in df else None,
    }


def category_table(df: pd.DataFrame) -> list[dict]:
    g = df.groupby("category").agg(n=("article_id", "count"), pv=("pv", "sum"), median_pv=("pv", "median"))
    return g.reset_index().sort_values("pv", ascending=False).to_dict(orient="records")


def build(month: str, top_n: int = 20) -> dict:
    dates = month_dates(month)
    df = load_dataset(dates)
    if df.empty:
        raise ValueError(f"{month} 데이터가 없습니다.")
    model_dates = [d for d in storage.list_dates("model") if d <= dates[-1]]
    model = storage.read_json(config.PATH_MODEL.format(date=model_dates[-1])) if model_dates else {}
    payload = {
        "month": month,
        "kpi": kpi(df),
        "by_category": category_table(df),
        "top_articles": df.sort_values("pv", ascending=False).head(top_n)[
            ["article_id", "title", "category", "pv"]].to_dict(orient="records"),
        "effects": model.get("effects", {}),
        "summary": model.get("summary", {}),
        "metrics": model.get("metrics", {}),
    }
    storage.write_json(config.PATH_MONTH.format(month=month), payload)
    log.info("월간 리포트 %s: %d건", month, len(df))
    return payload
