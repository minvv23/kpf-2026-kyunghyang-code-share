"""EDA 묶음 실행: 그림과 요약표를 한 번에 만든다."""
import os

from .. import config
from ..build_dataset import load_dataset
from ..extract_attributes import NUMERIC_ATTRS
from ..text_features import BASIC_FEATS, basic_features
from ..utils.date_utils import daterange
from ..utils.io_utils import write_csv
from ..utils.logging_utils import get_logger
from . import correlation, distribution, time_patterns

log = get_logger(__name__)


def run(start: str, end: str, out_dir: str = "./eda_out"):
    df = load_dataset(daterange(start, end))
    if df.empty:
        log.warning("데이터 없음: %s ~ %s", start, end)
        return None
    df = basic_features(df)
    os.makedirs(out_dir, exist_ok=True)
    outputs = []

    desc = distribution.describe(df)
    write_csv(desc.reset_index().to_dict(orient="records"), os.path.join(out_dir, "describe.csv"))
    for col in ("pv", "stay_sec"):
        if col in df:
            outputs.append(distribution.histogram(df, col, os.path.join(out_dir, f"hist_{col}.png")))
    if "category" in df:
        outputs.append(distribution.boxplot_by(df, "pv", "category", os.path.join(out_dir, "box_pv_category.png")))

    feats = [c for c in NUMERIC_ATTRS + BASIC_FEATS if c in df]
    corr = correlation.correlation_matrix(df, feats + ["pv"])
    outputs.append(correlation.heatmap(corr, os.path.join(out_dir, "corr.png")))

    if "published_at" in df:
        outputs.append(time_patterns.plot_hourly(df, os.path.join(out_dir, "hourly_pv.png")))
    outputs.append(time_patterns.plot_daily(df, os.path.join(out_dir, "daily_pv.png")))
    log.info("EDA %d개 산출물 → %s", len(outputs), out_dir)
    return outputs
