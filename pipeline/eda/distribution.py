"""성과 지표 분포."""
import numpy as np
import pandas as pd

from .plotting import plt, save


def describe(df: pd.DataFrame, cols=("pv", "stay_sec", "portal_inflow")) -> pd.DataFrame:
    cols = [c for c in cols if c in df]
    desc = df[cols].describe(percentiles=[.1, .25, .5, .75, .9, .99]).T
    desc["zero_share"] = [(df[c] == 0).mean() for c in cols]
    return desc


def histogram(df: pd.DataFrame, col: str, path: str, log: bool = True, bins: int = 50):
    v = df[col].dropna()
    if log:
        v = np.log1p(v)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(v, bins=bins, color="#4C72B0", alpha=.85)
    ax.set_xlabel(f"log(1+{col})" if log else col)
    ax.set_ylabel("기사 수")
    ax.set_title(f"{col} 분포")
    return save(fig, path)


def boxplot_by(df: pd.DataFrame, col: str, by: str, path: str, log: bool = True):
    groups = [(k, np.log1p(g[col].dropna()) if log else g[col].dropna()) for k, g in df.groupby(by)]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.boxplot([g for _, g in groups], labels=[k for k, _ in groups], showfliers=False)
    ax.set_ylabel(f"log(1+{col})" if log else col)
    ax.set_title(f"{by}별 {col}")
    return save(fig, path)
