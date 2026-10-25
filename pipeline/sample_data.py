"""동작 확인용 가상 데이터 생성기.

실제 기사·성과와 무관한 무작위 데이터다. 각 단계 입출력 형식을 확인하는 용도로만 쓴다.
"""
import random
from datetime import datetime, timedelta

from . import config, storage
from .extract_attributes import TOPICS
from .utils.date_utils import daterange

CATEGORIES = ["정치", "경제", "사회", "국제", "문화", "스포츠"]
WORDS = ["정부", "시장", "발표", "지역", "주민", "조사", "결과", "계획", "논의", "확대", "증가", "감소", "예정", "관계자"]


def _sentence(rng):
    return " ".join(rng.choice(WORDS) for _ in range(rng.randint(6, 14))) + "다."


def make_article(rng, date: str, i: int) -> dict:
    ts = datetime.strptime(date, "%Y%m%d") + timedelta(minutes=rng.randint(0, 24 * 60 - 1))
    body = "\n".join(" ".join(_sentence(rng) for _ in range(rng.randint(2, 5))) for _ in range(rng.randint(3, 10)))
    return {
        "article_id": f"{date}{i:05d}",
        "title": ("[속보] " if rng.random() < .05 else "") + " ".join(rng.choice(WORDS) for _ in range(5)),
        "body": body,
        "author": f"기자{rng.randint(1, 50)}",
        "published_at": ts.isoformat(),
        "category": rng.choice(CATEGORIES),
    }


def make_metric(rng, article: dict, date: str) -> dict:
    pv = int(rng.lognormvariate(5, 1.2))
    return {
        "article_id": article["article_id"],
        "stat_date": date,
        "pv": pv,
        "stay_sec": round(rng.uniform(5, 90), 1),
        "portal_inflow": int(pv * rng.uniform(0, 3)) if rng.random() < .3 else 0,
    }


def make_attributes(rng) -> dict:
    return {"topic": rng.choice(TOPICS), "sentiment": rng.randint(1, 5), "sensational": rng.randint(1, 5),
            "readability": rng.randint(1, 5), "objectivity": rng.randint(1, 5), "has_numbers": rng.randint(0, 1)}


def generate(start: str, end: str, per_day: int = 50, seed: int = 0, with_attributes: bool = True):
    rng = random.Random(seed)
    for d in daterange(start, end):
        arts = [make_article(rng, d, i) for i in range(per_day)]
        if with_attributes:
            for a in arts:
                a.update(make_attributes(rng))
        storage.write_json(config.PATH_ARTICLES.format(date=d), arts)
        storage.write_json(config.PATH_METRICS.format(date=d), [make_metric(rng, a, d) for a in arts])
    return len(daterange(start, end)) * per_day
