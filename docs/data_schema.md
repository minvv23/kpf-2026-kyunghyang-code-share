# 데이터 형식

## 1. 기사 메타데이터 (`articles/YYYYMMDD.json`)

| 필드 | 형식 | 필수 | 설명 |
|---|---|---|---|
| `article_id` | 문자열 | O | 기사 고유 ID (URL을 넣어도 숫자 ID로 정규화) |
| `title` | 문자열 | O | 제목 |
| `body` | 문자열 | O | 본문 |
| `author` | 문자열 |  | 작성자 |
| `published_at` | 문자열 |  | 게재 시각 (ISO 8601) |
| `category` | 문자열 |  | 섹션/카테고리 |

## 2. 성과 지표 (`metrics/YYYYMMDD.json`)

| 필드 | 형식 | 필수 | 설명 |
|---|---|---|---|
| `article_id` | 문자열 | O | 기사 ID |
| `pv` | 숫자 | O | 조회수 |
| `stay_sec` | 숫자 |  | 평균 체류시간(초) |
| `portal_inflow` | 숫자 |  | 포털 경유 유입 |
| `stat_date` | 문자열 |  | 집계일 |

## 3. 기사 단위 병합본 (`dataset/YYYYMMDD.json`)

기사 메타데이터 + 집계 기간 합산 성과(`pv`, `stay_sec`, `portal_inflow`) + LLM 속성
(`topic`, `sentiment`, `sensational`, `readability`, `objectivity`, `has_numbers`).

## 4. 모델링 결과 (`model/YYYYMMDD.json`)

```json
{
  "asof": "20261031",
  "metrics":    { "pv": { "n_train": 0, "n_test": 0, "mae": 0.0, "rmse": 0.0, "r2": 0.0, "mape": 0.0 } },
  "importance": { "pv": [ { "feature": "log_body_len", "importance": 0.0 } ] },
  "effects":    { "pv": [ { "var": "sensational", "label": "제목 자극성", "coef": 0.0, "sig": "***" } ] },
  "summary":    { "pv": "요약문" },
  "models":     { "pv": "<LightGBM model string>" }
}
```

## 5. 월간 리포트 (`report/month_YYYYMM.json`)

| 필드 | 설명 |
|---|---|
| `month` | YYYYMM |
| `kpi` | 기사 수, 조회수 합계·평균·중앙값, 체류시간 중앙값 |
| `by_category` | 분야별 기사 수·조회수 |
| `top_articles` | 조회수 상위 기사 |
| `effects`, `summary`, `metrics` | 해당 월 마지막 모델링 결과 |
