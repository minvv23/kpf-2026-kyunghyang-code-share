from pipeline.utils import text_utils as tu


def test_normalize_article_id_from_url():
    assert tu.normalize_article_id("https://example.com/article/202610140001") == "202610140001"


def test_normalize_article_id_plain():
    assert tu.normalize_article_id(" abc ") == "abc"


def test_strip_html():
    assert tu.collapse_spaces(tu.strip_html("<p>가 &amp; 나</p>")) == "가 & 나"


def test_remove_emails():
    assert "@" not in tu.remove_emails("문의 test@example.com 로")


def test_bracket_tag():
    assert tu.bracket_tag("[속보] 제목") == "속보"
    assert tu.bracket_tag("제목") is None


def test_count_sentences():
    assert tu.count_sentences("첫 문장이다. 둘째 문장이다.") == 2


def test_count_paragraphs():
    assert tu.count_paragraphs("문단1\n\n문단2\n문단3") == 3


def test_truncate():
    assert tu.truncate("가나다라마", 3) == "가나…"
