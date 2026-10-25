"""기사 메타데이터와 성과 지표를 기사 ID 기준으로 병합한다."""
from datetime import datetime, timedelta

import pandas as pd

from . import config, storage
from .utils.logging_utils import get_logger
from .utils.text_utils import normalize_article_id
from .utils.validators import validate_articles, validate_metrics

log = get_logger(__name__)

METRIC_COLS = ["pv", "stay_sec", "portal_inflow"]


def date_range(start: str, days: int):
    d0 = datetime.strptime(start, "%Y%m%d")
    return [(d0 + timedelta(days=i)).strftime("%Y%m%d") for i in range(max(days, 1))]


def load_articles(date: str) -> pd.DataFrame:
    rows = storage.read_json(config.PATH_ARTICLES.format(date=date))
    validate_articles(rows)
    df = pd.DataFrame(rows)
    df["article_id"] = df["article_id"].map(normalize_article_id)
    before = len(df)
    df = df.drop_duplicates("article_id")
    if len(df) < before:
        log.info("중복 기사 %d건 제거", before - len(df))
    return df


def load_metrics(date: str) -> pd.DataFrame:
    rel = config.PATH_METRICS.format(date=date)
    if not storage.exists(rel):
        log.warning("성과 지표 없음: %s", date)
        return pd.DataFrame(columns=["article_id"] + METRIC_COLS)
    rows = storage.read_json(rel)
    validate_metrics(rows)
    df = pd.DataFrame(rows)
    df["article_id"] = df["article_id"].map(normalize_article_id)
    return df


def aggregate_metrics(frames) -> pd.DataFrame:
    if not frames:
        return pd.DataFrame(columns=["article_id"] + METRIC_COLS)
    df = pd.concat(frames, ignore_index=True)
    return df.groupby("article_id", as_index=False).agg(
        pv=("pv", "sum"), stay_sec=("stay_sec", "mean"), portal_inflow=("portal_inflow", "sum"))


def build(date: str) -> pd.DataFrame:
    """date에 발행된 기사에 집계 기간(LABEL_DAYS) 동안의 성과를 붙인다."""
    arts = load_articles(date)
    perf = aggregate_metrics([load_metrics(d) for d in date_range(date, config.LABEL_DAYS)])
    out = arts.merge(perf, on="article_id", how="left")
    out[["pv", "portal_inflow"]] = out[["pv", "portal_inflow"]].fillna(0)
    out["publish_date"] = date
    storage.write_json(config.PATH_DATASET.format(date=date), out.to_dict(orient="records"))
    log.info("dataset %s: %d건", date, len(out))
    return out


def load_dataset(dates) -> pd.DataFrame:
    frames = []
    for d in dates:
        rel = config.PATH_DATASET.format(date=d)
        if storage.exists(rel):
            frames.append(pd.DataFrame(storage.read_json(rel)))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
