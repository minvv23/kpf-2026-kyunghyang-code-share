"""저장소 점검: 날짜별 파일 유무와 건수를 표로 출력한다.

python scripts/check_storage.py --start 20261001 --end 20261014
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pipeline import config, storage  # noqa: E402
from pipeline.extract_attributes import ATTR_COLS  # noqa: E402
from pipeline.utils.date_utils import daterange  # noqa: E402

KINDS = [("articles", config.PATH_ARTICLES), ("metrics", config.PATH_METRICS), ("dataset", config.PATH_DATASET)]


def count(rel):
    if not storage.exists(rel):
        return None
    rows = storage.read_json(rel)
    return len(rows) if isinstance(rows, list) else 1


def attr_coverage(date):
    rel = config.PATH_DATASET.format(date=date)
    if not storage.exists(rel):
        return None
    rows = storage.read_json(rel)
    if not rows:
        return 0.0
    done = sum(1 for r in rows if all(c in r for c in ATTR_COLS))
    return done / len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    a = ap.parse_args()

    print(f"{'date':10} " + " ".join(f"{k:>9}" for k, _ in KINDS) + f" {'attr%':>7}")
    for d in daterange(a.start, a.end):
        cells = []
        for _, pattern in KINDS:
            n = count(pattern.format(date=d))
            cells.append(f"{'-' if n is None else n:>9}")
        cov = attr_coverage(d)
        print(f"{d:10} " + " ".join(cells) + f" {'-' if cov is None else f'{cov:.0%}':>7}")


if __name__ == "__main__":
    main()
