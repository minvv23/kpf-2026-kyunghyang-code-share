"""파일 입출력 보조."""
import csv
import json
import os

import pandas as pd


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)
    return path


def read_csv_records(path: str, id_col: str = "article_id") -> list[dict]:
    df = pd.read_csv(path, dtype={id_col: str})
    return df.where(pd.notnull(df), None).to_dict(orient="records")


def write_csv(rows: list[dict], path: str):
    if not rows:
        return
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def write_json_file(obj, path: str, indent: int = 2):
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, default=str)


def read_json_file(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def chunked(seq, size: int):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]
