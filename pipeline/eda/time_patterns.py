"""발행 시각·요일별 패턴."""
import pandas as pd

from .plotting import plt, save

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def by_hour(df: pd.DataFrame, target: str = "pv") -> pd.DataFrame:
    ts = pd.to_datetime(df["published_at"], errors="coerce")
    return df.assign(hour=ts.dt.hour).groupby("hour")[target].agg(["count", "median", "mean"]).reset_index()


def by_weekday(df: pd.DataFrame, target: str = "pv") -> pd.DataFrame:
    ts = pd.to_datetime(df["published_at"], errors="coerce")
    out = df.assign(wd=ts.dt.weekday).groupby("wd")[target].agg(["count", "median", "mean"]).reset_index()
    out["weekday"] = out["wd"].map(lambda i: WEEKDAYS[int(i)] if pd.notnull(i) else "")
    return out


def daily_series(df: pd.DataFrame, target: str = "pv") -> pd.DataFrame:
    return df.groupby("publish_date")[target].agg(["count", "sum", "median"]).reset_index()


def plot_hourly(df: pd.DataFrame, path: str, target: str = "pv"):
    t = by_hour(df, target)
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.bar(t["hour"], t["median"], color="#55A868")
    ax.set_xlabel("발행 시각")
    ax.set_ylabel(f"{target} 중앙값")
    ax.set_title(f"발행 시각별 {target}")
    return save(fig, path)


def plot_daily(df: pd.DataFrame, path: str, target: str = "pv"):
    t = daily_series(df, target)
    fig, ax = plt.subplots(figsize=(9, 3.5))
    ax.plot(pd.to_datetime(t["publish_date"]), t["sum"], marker="o", ms=3)
    ax.set_ylabel(f"{target} 합계")
    ax.set_title(f"일별 {target}")
    fig.autofmt_xdate()
    return save(fig, path)
