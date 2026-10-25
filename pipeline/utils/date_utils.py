"""날짜 처리."""
from datetime import date, datetime, timedelta

FMT = "%Y%m%d"


def parse(value: str) -> date:
    return datetime.strptime(value, FMT).date()


def fmt(d: date) -> str:
    return d.strftime(FMT)


def today() -> str:
    return fmt(date.today())


def add_days(value: str, n: int) -> str:
    return fmt(parse(value) + timedelta(days=n))


def daterange(start: str, end: str):
    """start ~ end (양끝 포함) 날짜 목록."""
    d, last = parse(start), parse(end)
    out = []
    while d <= last:
        out.append(fmt(d))
        d += timedelta(days=1)
    return out


def month_of(value: str) -> str:
    return value[:6]


def prev_month(month: str) -> str:
    y, m = int(month[:4]), int(month[4:6])
    return f"{y - 1}12" if m == 1 else f"{y}{m - 1:02d}"


def next_month(month: str) -> str:
    y, m = int(month[:4]), int(month[4:6])
    return f"{y + 1}01" if m == 12 else f"{y}{m + 1:02d}"


def month_label(month: str) -> str:
    return f"{month[:4]}년 {int(month[4:6])}월"
