"""입력 레코드 형식 검사."""
from datetime import datetime

from .exceptions import ValidationError

ARTICLE_REQUIRED = {"article_id": str, "title": str, "body": str}
ARTICLE_OPTIONAL = {"author": str, "published_at": str, "category": str}
METRIC_REQUIRED = {"article_id": str, "pv": (int, float)}
METRIC_OPTIONAL = {"stay_sec": (int, float), "portal_inflow": (int, float), "stat_date": str}


def _check(rows, required, optional, label, strict=False):
    errors = []
    if not isinstance(rows, list):
        raise ValidationError(f"{label}: 리스트가 아닙니다")
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            errors.append(f"[{i}] dict 아님")
            continue
        for k, t in required.items():
            if k not in r or r[k] is None:
                errors.append(f"[{i}] {k} 누락")
            elif not isinstance(r[k], t):
                errors.append(f"[{i}] {k} 형식 오류")
        for k, t in optional.items():
            if k in r and r[k] is not None and not isinstance(r[k], t):
                errors.append(f"[{i}] {k} 형식 오류")
        if strict:
            extra = set(r) - set(required) - set(optional)
            if extra:
                errors.append(f"[{i}] 정의되지 않은 필드: {sorted(extra)}")
    if errors:
        raise ValidationError(f"{label} 검사 실패", errors)
    return True


def validate_articles(rows, strict=False):
    return _check(rows, ARTICLE_REQUIRED, ARTICLE_OPTIONAL, "articles", strict)


def validate_metrics(rows, strict=False):
    return _check(rows, METRIC_REQUIRED, METRIC_OPTIONAL, "metrics", strict)


def validate_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y%m%d")
    except (TypeError, ValueError):
        raise ValidationError(f"날짜 형식 오류: {value!r} (YYYYMMDD)")
    return value


def validate_month(value: str) -> str:
    try:
        datetime.strptime(value + "01", "%Y%m%d")
    except (TypeError, ValueError):
        raise ValidationError(f"월 형식 오류: {value!r} (YYYYMM)")
    return value
