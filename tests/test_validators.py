import pytest

from pipeline.utils.exceptions import ValidationError
from pipeline.utils.validators import validate_articles, validate_date, validate_metrics, validate_month


def test_articles_ok(sample_articles):
    assert validate_articles(sample_articles)


def test_articles_missing_title():
    with pytest.raises(ValidationError):
        validate_articles([{"article_id": "1", "body": "x"}])


def test_metrics_ok(sample_metrics):
    assert validate_metrics(sample_metrics)


def test_metrics_wrong_type():
    with pytest.raises(ValidationError):
        validate_metrics([{"article_id": "1", "pv": "많음"}])


def test_date_and_month():
    assert validate_date("20261014") == "20261014"
    assert validate_month("202610") == "202610"
    with pytest.raises(ValidationError):
        validate_date("2026-10-14")
