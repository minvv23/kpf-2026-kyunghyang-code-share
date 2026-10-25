"""요인별 효과 크기 (표준화 선형회귀)."""
import numpy as np
import pandas as pd
import statsmodels.api as sm

from .extract_attributes import NUMERIC_ATTRS
from .text_features import BASIC_FEATS

LABELS = {
    "sentiment": "논조", "sensational": "제목 자극성", "readability": "읽기 쉬움", "objectivity": "객관성",
    "has_numbers": "수치 정보", "title_len": "제목 길이", "log_body_len": "본문 길이",
    "n_sentences": "문장 수", "n_paragraphs": "문단 수", "has_bracket_tag": "말머리 표기",
}
VARS = [v for v in NUMERIC_ATTRS + ["has_numbers"] + BASIC_FEATS if v in LABELS]


def significance(p: float) -> str:
    return "***" if p < .01 else "**" if p < .05 else "*" if p < .1 else "n.s."


def fit_effects(df: pd.DataFrame, target: str):
    cols = [v for v in VARS if v in df]
    d = df.dropna(subset=cols + [target])
    mean, std = d[cols].mean(), d[cols].std().replace(0, 1)
    Z = (d[cols] - mean) / std
    res = sm.OLS(np.log1p(d[target]), sm.add_constant(Z)).fit()
    effects = [{"var": v, "label": LABELS[v], "coef": round(float(res.params[v]), 4),
                "sig": significance(float(res.pvalues[v]))} for v in cols]
    effects.sort(key=lambda e: -abs(e["coef"]))
    return {"effects": effects, "n": int(res.nobs), "r2": round(float(res.rsquared), 4)}


def summary_text(fit: dict, target_label: str) -> str:
    sig = [e for e in fit["effects"] if e["sig"] != "n.s."]
    if not sig:
        return f"이번 기간 {target_label}과(와) 뚜렷한 관련을 보인 요인은 없었습니다."
    top = sig[0]
    word = "높을수록" if top["coef"] > 0 else "낮을수록"
    return f"{top['label']}이(가) {word} {target_label}이(가) 높은 경향이 있었습니다. (N={fit['n']:,}, R²={fit['r2']})"
