"""설정 로더.

우선순위: 환경변수 > config/settings.yaml > 기본값
"""
import json
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _load_yaml(path):
    if not os.path.exists(path):
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_YAML = _load_yaml(os.environ.get("SETTINGS_FILE", os.path.join(_ROOT, "config", "settings.yaml")))


def _get(key, default=None, cast=str):
    if key in os.environ and os.environ[key] != "":
        raw = os.environ[key]
    elif key.lower() in _YAML:
        raw = _YAML[key.lower()]
    else:
        return default
    try:
        return cast(raw)
    except (TypeError, ValueError):
        return default


STORAGE_ROOT = _get("STORAGE_ROOT", "./data")
LOG_LEVEL = _get("LOG_LEVEL", "INFO")

OPENAI_API_KEY = _get("OPENAI_API_KEY", "")
LLM_MODEL = _get("LLM_MODEL", "")
LLM_MAX_CHARS = _get("LLM_MAX_CHARS", 4000, int)
LLM_RETRIES = _get("LLM_RETRIES", 3, int)

# 학습 기간·모델 설정은 운영 환경에서 주입한다.
LABEL_DAYS = _get("LABEL_DAYS", 1, int)            # 성과 집계 기간(일)
TRAIN_DAYS = _get("TRAIN_DAYS", 0, int)
INTERP_DAYS = _get("INTERP_DAYS", 0, int)
HOLDOUT_DAYS = _get("HOLDOUT_DAYS", 0, int)
MODEL_PARAMS = _get("MODEL_PARAMS", {}, lambda v: v if isinstance(v, dict) else json.loads(v))
N_ROUNDS = _get("N_ROUNDS", 100, int)
RANDOM_STATE = 0

# 저장소 안의 경로 규칙
PATH_ARTICLES = "articles/{date}.json"          # 기사 메타데이터
PATH_METRICS = "metrics/{date}.json"            # 성과 지표
PATH_DATASET = "dataset/{date}.json"            # 기사 단위 병합본 (+ 속성)
PATH_MODEL = "model/{date}.json"                # 모델링 결과
PATH_MONTH = "report/month_{month}.json"        # 월간 리포트
PATH_FIGURES = "figures/{name}.png"             # EDA 그림

# 예측 대상
TARGETS = {
    "pv": "조회수",
    "stay_sec": "체류시간(초)",
    "portal_inflow": "포털 유입",
}
