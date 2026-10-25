# kpf-2026-kyunghyang-code-share

2026년 한국언론진흥재단 디지털 미디어 서비스 개발 지원 사업으로 개발한
**AI 기반 '기사 속성 수치화'를 활용한 기사 성과 예측 및 컨텐츠 전략 인텔리전스 시스템**(경향신문)의 공개 소스코드입니다.

기사 텍스트에서 LLM으로 속성을 뽑아 수치화하고, 그 속성과 기본 텍스트 변수로 기사별 조회수·체류시간·포털 유입을 예측하며,
요인별 관련성을 월간 리포트로 정리하는 흐름을 담고 있습니다.
다른 언론사가 자사 데이터에 맞춰 바꿔 쓸 수 있도록 기본형(reference implementation)으로 정리했습니다.

## 구성

```
pipeline/
  config.py               설정 로더 (환경변수 > config/settings.yaml > 기본값)
  storage.py              저장소 추상화 (로컬 폴더 / 클라우드 버킷)
  collect_metrics.py      성과 지표 수집 인터페이스 (통계 시스템 연동부는 각사 구현)
  build_dataset.py        기사 메타데이터 + 성과 지표를 기사 ID 기준으로 병합
  extract_attributes.py   LLM 구조화 출력으로 기사 속성 추출
  text_features.py        제목·본문 길이, 문장·문단 수 등 기본 변수
  train_model.py          성과 예측 모델 학습·평가 (LightGBM 회귀)
  interpret.py            표준화 선형회귀로 요인별 관련성 정리
  monthly_report.py       달력 월 단위 리포트 집계
  sample_data.py          동작 확인용 가상 데이터 생성
  run_pipeline.py         명령행 진입점
  utils/                  로깅, 예외, 입력 검사, 텍스트 정리, 날짜, 입출력, 평가 지표
  eda/                    분포·상관·시간대 패턴 그림과 요약표
scripts/
  check_storage.py        날짜별 적재 현황 점검
  export_report_csv.py    월간 리포트를 CSV로 내보내기
  compare_months.py       두 달 리포트 비교
tests/                    단위 테스트 (pytest)
config/
  settings.example.yaml   설정 파일 예시
web/
  index.html              월간 리포트 웹 화면 기본 틀
docs/
  architecture.md         처리 흐름
  data_schema.md          입력·출력 데이터 형식
```

## 설치

Python 3.11 이상을 권장합니다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                  # 값 채우기
cp config/settings.example.yaml config/settings.yaml  # 선택
```

## 환경 설정

| 변수 | 설명 |
|---|---|
| `STORAGE_ROOT` | 데이터 저장 위치. 로컬 폴더 경로 또는 `gs://버킷/경로` |
| `OPENAI_API_KEY` | 속성 추출에 쓰는 LLM API 키 |
| `LLM_MODEL` | 속성 추출 모델명 |
| `LABEL_DAYS` | 발행 후 성과를 합산할 기간(일) |
| `TRAIN_DAYS`, `INTERP_DAYS`, `HOLDOUT_DAYS` | 학습·해석·검증 기간(일) |
| `MODEL_PARAMS`, `N_ROUNDS` | LightGBM 하이퍼파라미터(JSON), 학습 횟수 |

통계 시스템 연동 정보, 계정, 서버 주소 등은 저장소에 포함하지 않았습니다.
`pipeline/collect_metrics.py`의 `MetricsSource`를 각사 환경에 맞게 구현해 사용하세요.

## 실행

```bash
# 가상 데이터로 흐름 확인
python -m pipeline.run_pipeline sample --start 20260901 --end 20261031
python -m pipeline.run_pipeline backfill --start 20260901 --end 20261031 --skip-extract

# 실제 데이터: 하루치 적재 → 속성 추출
python -m pipeline.run_pipeline collect --date 20261014 --articles data/articles.csv --site data/site.csv
python -m pipeline.run_pipeline extract --date 20261014

# 모델 학습·해석, 월간 리포트
python -m pipeline.run_pipeline model --asof 20261031
python -m pipeline.run_pipeline report --month 202610

# 탐색적 분석 그림
python -m pipeline.run_pipeline eda --start 20261001 --end 20261031 --out ./eda_out

# 보조 스크립트
python scripts/check_storage.py --start 20261001 --end 20261031
python scripts/export_report_csv.py --month 202610
python scripts/compare_months.py --a 202609 --b 202610
```

테스트:

```bash
pytest -q
```

## 웹 화면

`web/index.html`은 메뉴 구성(월간 대시보드, 가중치 트렌드, 예측 시뮬레이터, 속성 추출 결과)만 담은 기본 틀입니다.
월간 리포트 JSON(`docs/data_schema.md`)을 받아 그리도록 각사 환경에 맞게 연결합니다.

## 라이선스

MIT License. `LICENSE` 파일을 참고하세요.
