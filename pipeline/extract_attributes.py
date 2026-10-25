"""LLM 구조화 출력으로 기사 속성을 점수화한다.

아래 항목과 지침은 일반적인 예시다. 실제 운영 시에는 각사 편집 기준에 맞춰 바꿔 쓴다.
"""
import time
from typing import Literal

from pydantic import BaseModel, Field

from . import config, storage
from .utils.logging_utils import get_logger
from .utils.text_utils import clean_text

log = get_logger(__name__)

TOPICS = ("정치", "경제", "사회", "국제", "문화", "스포츠", "IT", "기타")


class ArticleAttributes(BaseModel):
    topic: Literal[TOPICS] = Field(description="주제")
    sentiment: Literal[1, 2, 3, 4, 5] = Field(description="논조 (1 부정 ~ 5 긍정)")
    sensational: Literal[1, 2, 3, 4, 5] = Field(description="제목 자극성")
    readability: Literal[1, 2, 3, 4, 5] = Field(description="읽기 쉬움")
    objectivity: Literal[1, 2, 3, 4, 5] = Field(description="객관성")
    has_numbers: bool = Field(description="수치 정보 포함 여부")


ATTR_COLS = [c for c in ArticleAttributes.model_fields if c != "topic"]
NUMERIC_ATTRS = ["sentiment", "sensational", "readability", "objectivity"]

GUIDELINE = "다음 뉴스 기사를 읽고 각 항목을 평가하라. 출력은 JSON 스키마를 따른다."


def _client():
    from openai import OpenAI
    return OpenAI(api_key=config.OPENAI_API_KEY)


def build_messages(title: str, body: str):
    return [
        {"role": "system", "content": GUIDELINE},
        {"role": "user", "content": f"제목: {clean_text(title)}\n\n본문: {clean_text(body)[:config.LLM_MAX_CHARS]}"},
    ]


def extract_one(client, title: str, body: str) -> dict:
    for attempt in range(config.LLM_RETRIES):
        try:
            resp = client.chat.completions.parse(
                model=config.LLM_MODEL, messages=build_messages(title, body), response_format=ArticleAttributes)
            out = resp.choices[0].message.parsed.model_dump()
            out["has_numbers"] = int(out["has_numbers"])
            return out
        except Exception as e:  # noqa: BLE001
            log.warning("추출 실패 (%d/%d): %s", attempt + 1, config.LLM_RETRIES, e)
            time.sleep(2 ** attempt)
    raise RuntimeError("속성 추출 재시도 초과")


def run(date: str, limit: int | None = None) -> int:
    rel = config.PATH_DATASET.format(date=date)
    rows = storage.read_json(rel)
    client = _client()
    done = 0
    for r in rows[:limit] if limit else rows:
        if all(c in r for c in ATTR_COLS):
            continue
        try:
            r.update(extract_one(client, r.get("title", ""), r.get("body", "")))
            done += 1
        except RuntimeError as e:
            log.error("[skip] %s: %s", r.get("article_id"), e)
    storage.write_json(rel, rows)
    log.info("속성 추출 %s: %d건", date, done)
    return done
