"""회귀 평가 지표."""
import numpy as np


def mae(y, p):
    return float(np.mean(np.abs(np.asarray(y) - np.asarray(p))))


def rmse(y, p):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(p)) ** 2)))


def r2(y, p):
    y, p = np.asarray(y, dtype=float), np.asarray(p, dtype=float)
    ss_res = np.sum((y - p) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0


def mape(y, p, min_y=1.0):
    y, p = np.asarray(y, dtype=float), np.asarray(p, dtype=float)
    mask = y >= min_y
    if not mask.any():
        return float("nan")
    return float(np.mean(np.abs((y[mask] - p[mask]) / y[mask])) * 100)


def regression_report(y, p) -> dict:
    return {"mae": round(mae(y, p), 3), "rmse": round(rmse(y, p), 3),
            "r2": round(r2(y, p), 4), "mape": round(mape(y, p), 2)}
