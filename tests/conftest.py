import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def tmp_storage(tmp_path, monkeypatch):
    from pipeline import config
    monkeypatch.setattr(config, "STORAGE_ROOT", str(tmp_path))
    return tmp_path


@pytest.fixture
def sample_articles():
    return [
        {"article_id": "https://example.com/article/202610140001", "title": "[속보] 제목 하나", "body": "첫 문장이다. 둘째 문장이다.",
         "published_at": "2026-10-14T09:00:00", "category": "사회"},
        {"article_id": "202610140002", "title": "제목 둘", "body": "본문.\n\n다른 문단.", "published_at": "2026-10-14T13:30:00",
         "category": "경제"},
    ]


@pytest.fixture
def sample_metrics():
    return [
        {"article_id": "202610140001", "stat_date": "20261014", "pv": 120, "stay_sec": 30.0, "portal_inflow": 0},
        {"article_id": "202610140002", "stat_date": "20261014", "pv": 45, "stay_sec": 12.5, "portal_inflow": 10},
    ]
