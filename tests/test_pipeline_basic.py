import pandas as pd

from pipeline import build_dataset, config, monthly_report, storage, text_features
from pipeline.utils import date_utils, metrics


def test_build_dataset(tmp_storage, sample_articles, sample_metrics):
    storage.write_json(config.PATH_ARTICLES.format(date="20261014"), sample_articles)
    storage.write_json(config.PATH_METRICS.format(date="20261014"), sample_metrics)
    df = build_dataset.build("20261014")
    assert len(df) == 2
    assert set(df["article_id"]) == {"202610140001", "202610140002"}
    assert df.loc[df["article_id"] == "202610140001", "pv"].iloc[0] == 120


def test_basic_features(sample_articles):
    df = text_features.basic_features(pd.DataFrame(sample_articles))
    assert {"title_len", "log_body_len", "n_sentences", "hour"} <= set(df.columns)
    assert df["has_bracket_tag"].tolist() == [1, 0]


def test_month_dates():
    assert monthly_report.month_dates("202602")[-1] == "20260228"


def test_date_utils():
    assert date_utils.add_days("20261031", 1) == "20261101"
    assert date_utils.prev_month("202601") == "202512"
    assert date_utils.daterange("20261001", "20261003") == ["20261001", "20261002", "20261003"]


def test_regression_report():
    rep = metrics.regression_report([1, 2, 3], [1, 2, 4])
    assert rep["mae"] > 0 and rep["r2"] < 1
