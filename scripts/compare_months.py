"""두 달 리포트의 KPI와 요인 효과를 나란히 비교한다.

python scripts/compare_months.py --a 202609 --b 202610
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pipeline import config, storage  # noqa: E402


def load(month):
    return storage.read_json(config.PATH_MONTH.format(month=month))


def fmt(v):
    return f"{v:,.1f}" if isinstance(v, float) else f"{v:,}" if isinstance(v, int) else str(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--target", default="pv")
    x = ap.parse_args()
    ra, rb = load(x.a), load(x.b)

    print(f"[KPI] {x.a} vs {x.b}")
    for k in ra["kpi"]:
        va, vb = ra["kpi"].get(k), rb["kpi"].get(k)
        print(f"  {k:18} {fmt(va):>14} {fmt(vb):>14}")

    print(f"\n[요인 효과: {x.target}]")
    ea = {e["var"]: e for e in ra.get("effects", {}).get(x.target, [])}
    eb = {e["var"]: e for e in rb.get("effects", {}).get(x.target, [])}
    for v in sorted(set(ea) | set(eb)):
        a_, b_ = ea.get(v, {}), eb.get(v, {})
        label = a_.get("label") or b_.get("label") or v
        print(f"  {label:12} {a_.get('coef', '-'):>10} {b_.get('coef', '-'):>10}")


if __name__ == "__main__":
    main()
