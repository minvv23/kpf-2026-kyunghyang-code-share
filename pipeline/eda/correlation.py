"""변수 간 상관."""
import numpy as np
import pandas as pd

from .plotting import plt, save


def correlation_matrix(df: pd.DataFrame, cols, method: str = "spearman") -> pd.DataFrame:
    cols = [c for c in cols if c in df]
    return df[cols].apply(pd.to_numeric, errors="coerce").corr(method=method)


def heatmap(corr: pd.DataFrame, path: str, title: str = "상관 행렬"):
    fig, ax = plt.subplots(figsize=(1 + .6 * len(corr), 1 + .5 * len(corr)))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns, rotation=60, ha="right")
    ax.set_yticks(range(len(corr)), corr.index)
    for i in range(len(corr)):
        for j in range(len(corr)):
            v = corr.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7)
    fig.colorbar(im, ax=ax, shrink=.8)
    ax.set_title(title)
    return save(fig, path)


def target_correlations(df: pd.DataFrame, features, target: str) -> pd.Series:
    corr = correlation_matrix(df, list(features) + [target])
    return corr[target].drop(target).sort_values(key=np.abs, ascending=False)
