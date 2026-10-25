"""기사 성과 지표 수집 인터페이스.

언론사마다 통계 시스템(웹 로그 분석 도구, 포털 언론사 통계 등)이 다르므로
실제 연동부는 MetricsSource를 상속해 각사 환경에 맞게 구현한다.
접속 주소·계정 정보는 코드에 넣지 말고 환경변수나 비밀 관리 도구로 주입한다.
"""
from dataclasses import dataclass, asdict
from typing import Iterable

from . import config, storage


@dataclass
class ArticleMetric:
    article_id: str
    stat_date: str          # YYYYMMDD
    pv: int = 0             # 자사 사이트 조회수
    stay_sec: float = 0.0   # 자사 사이트 평균 체류시간(초)
    portal_inflow: int = 0  # 포털 경유 유입 (집계 대상이 아니면 0)
    portal_ranked: bool = False


class MetricsSource:
    """통계 시스템 연동 기본 클래스."""

    def fetch_site_metrics(self, date: str) -> Iterable[ArticleMetric]:
        raise NotImplementedError("자사 사이트 통계 연동부를 구현하세요.")

    def fetch_portal_metrics(self, date: str) -> Iterable[ArticleMetric]:
        raise NotImplementedError("포털 통계 연동부를 구현하세요.")


class CsvMetricsSource(MetricsSource):
    """CSV로 내려받은 통계 파일을 읽는 예시 구현.

    site CSV 열: article_id, pv, stay_sec
    portal CSV 열: article_id, portal_inflow
    """

    def __init__(self, site_csv: str, portal_csv: str | None = None):
        self.site_csv, self.portal_csv = site_csv, portal_csv

    def fetch_site_metrics(self, date):
        import pandas as pd
        for r in pd.read_csv(self.site_csv, dtype={"article_id": str}).itertuples():
            yield ArticleMetric(r.article_id, date, int(r.pv), float(r.stay_sec))

    def fetch_portal_metrics(self, date):
        if not self.portal_csv:
            return []
        import pandas as pd
        return [ArticleMetric(r.article_id, date, portal_inflow=int(r.portal_inflow), portal_ranked=True)
                for r in pd.read_csv(self.portal_csv, dtype={"article_id": str}).itertuples()]


def collect(source: MetricsSource, date: str):
    """하루치 지표를 기사 ID 기준으로 합쳐 저장한다."""
    rows = {}
    for m in source.fetch_site_metrics(date):
        rows[m.article_id] = m
    for m in source.fetch_portal_metrics(date):
        base = rows.setdefault(m.article_id, ArticleMetric(m.article_id, date))
        base.portal_inflow, base.portal_ranked = m.portal_inflow, m.portal_ranked
    out = [asdict(m) for m in rows.values()]
    storage.write_json(config.PATH_METRICS.format(date=date), out)
    return len(out)
