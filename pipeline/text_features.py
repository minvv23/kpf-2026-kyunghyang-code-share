"""텍스트 기반 기본 변수."""
import numpy as np
import pandas as pd

from .utils.text_utils import count_sentences, count_paragraphs

BASIC_FEATS = ["title_len", "log_body_len", "n_sentences", "n_paragraphs", "has_bracket_tag"]


def basic_features(df: pd.DataFrame) -> pd.DataFrame:
    title = df["title"].fillna("")
    body = df["body"].fillna("")
    df["title_len"] = title.str.len()
    df["log_body_len"] = np.log1p(body.str.len())
    df["n_sentences"] = body.map(count_sentences)
    df["n_paragraphs"] = body.map(count_paragraphs)
    df["has_bracket_tag"] = title.str.match(r"^\s*\[").astype(int)
    if "published_at" in df:
        ts = pd.to_datetime(df["published_at"], errors="coerce")
        df["hour"] = ts.dt.hour.fillna(-1).astype(int)
        df["weekday"] = ts.dt.weekday.fillna(-1).astype(int)
    return df
