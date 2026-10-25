"""월간 리포트 JSON을 CSV 여러 장으로 내보낸다.

python scripts/export_report_csv.py --month 202610 --out ./export
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pipeline import config, storage  # noqa: E402
from pipeline.utils.io_utils import write_csv  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", required=True)
    ap.add_argument("--out", default="./export")
    a = ap.parse_args()

    rep = storage.read_json(config.PATH_MONTH.format(month=a.month))
    write_csv([rep["kpi"]], os.path.join(a.out, f"{a.month}_kpi.csv"))
    write_csv(rep.get("top_articles", []), os.path.join(a.out, f"{a.month}_top_articles.csv"))
    write_csv(rep.get("by_category", []), os.path.join(a.out, f"{a.month}_by_category.csv"))
    for target, rows in rep.get("effects", {}).items():
        write_csv(rows, os.path.join(a.out, f"{a.month}_effects_{target}.csv"))
    print(f"exported → {a.out}")


if __name__ == "__main__":
    main()
