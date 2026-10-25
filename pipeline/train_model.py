"""성과 예측 모델 학습·평가 (LightGBM 회귀)."""
import numpy as np
import pandas as pd

from . import config
from .extract_attributes import ATTR_COLS
from .text_features import BASIC_FEATS
from .utils.logging_utils import get_logger
from .utils.metrics import regression_report

log = get_logger(__name__)

NUM_FEATS = ATTR_COLS + BASIC_FEATS
CAT_FEATS = ["category", "topic"]

# 하이퍼파라미터는 각사 데이터에 맞춰 조정해 MODEL_PARAMS로 주입한다.
PARAMS = {"objective": "regression", "verbose": -1, **config.MODEL_PARAMS}


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    X = pd.DataFrame(index=df.index)
    for c in NUM_FEATS:
        X[c] = pd.to_numeric(df.get(c), errors="coerce")
    for c in CAT_FEATS:
        if c in df:
            X[c] = df[c].astype("category")
    return X


def split_by_date(df: pd.DataFrame, holdout_days: int):
    dates = sorted(df["publish_date"].unique())
    if holdout_days <= 0 or len(dates) <= holdout_days:
        n = max(1, len(df) // 5)
        return df.iloc[:-n], df.iloc[-n:]
    cut = dates[-holdout_days]
    return df[df["publish_date"] < cut], df[df["publish_date"] >= cut]


def train(df: pd.DataFrame, target: str):
    import lightgbm as lgb
    df = df.dropna(subset=[target]).sort_values("publish_date")
    tr, te = split_by_date(df, config.HOLDOUT_DAYS)
    model = lgb.train(PARAMS, lgb.Dataset(prepare(tr), np.log1p(tr[target])), num_boost_round=config.N_ROUNDS)
    pred = np.expm1(model.predict(prepare(te)))
    metrics = {"n_train": int(len(tr)), "n_test": int(len(te)), **regression_report(te[target].values, pred)}
    log.info("%s: %s", target, metrics)
    final = lgb.train(PARAMS, lgb.Dataset(prepare(df), np.log1p(df[target])), num_boost_round=config.N_ROUNDS)
    return final, metrics


def feature_importance(model) -> list[dict]:
    names = model.feature_name()
    gain = model.feature_importance(importance_type="gain")
    total = gain.sum() or 1
    rows = [{"feature": n, "importance": round(float(g / total), 4)} for n, g in zip(names, gain)]
    return sorted(rows, key=lambda r: -r["importance"])


def predict(model, df: pd.DataFrame) -> np.ndarray:
    return np.expm1(model.predict(prepare(df)))
