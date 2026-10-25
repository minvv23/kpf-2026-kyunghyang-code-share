"""텍스트 정리 함수."""
import html
import re
import unicodedata

_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")
_SENT = re.compile(r"(?<=[.!?。])\s+|(?<=다\.)\s*")
_BRACKET = re.compile(r"^\s*\[([^\]]+)\]")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_BYLINE = re.compile(r"\S+\s?기자\s*$")


def normalize_article_id(value) -> str:
    """URL이나 문자열에서 숫자 기사 ID만 남긴다."""
    m = re.search(r"(\d{6,})", str(value))
    return m.group(1) if m else str(value).strip()


def strip_html(text: str) -> str:
    return html.unescape(_TAG.sub(" ", text or ""))


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFC", text or "")


def collapse_spaces(text: str) -> str:
    return _SPACE.sub(" ", text or "").strip()


def remove_emails(text: str) -> str:
    return _EMAIL.sub("", text or "")


def remove_byline(text: str) -> str:
    lines = (text or "").splitlines()
    while lines and _BYLINE.search(lines[-1].strip()):
        lines.pop()
    return "\n".join(lines)


def clean_text(text: str) -> str:
    """HTML 제거 → 유니코드 정규화 → 이메일·바이라인 제거 → 공백 정리."""
    t = strip_html(text)
    t = normalize_unicode(t)
    t = remove_emails(t)
    t = remove_byline(t)
    return collapse_spaces(t)


def bracket_tag(title: str) -> str | None:
    """제목 맨 앞 말머리([...])를 돌려준다."""
    m = _BRACKET.match(title or "")
    return m.group(1) if m else None


def count_sentences(text: str) -> int:
    t = collapse_spaces(strip_html(text))
    if not t:
        return 0
    return len([s for s in _SENT.split(t) if s.strip()])


def count_paragraphs(text: str) -> int:
    return len([p for p in re.split(r"\n\s*\n|\n", text or "") if p.strip()])


def truncate(text: str, n: int, suffix: str = "…") -> str:
    text = text or ""
    return text if len(text) <= n else text[: max(0, n - len(suffix))] + suffix
