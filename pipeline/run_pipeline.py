"""실행 진입점.

python -m pipeline.run_pipeline sample   --start YYYYMMDD --end YYYYMMDD
python -m pipeline.run_pipeline collect  --date YYYYMMDD [--articles 기사.csv] [--site 통계.csv --portal 포털.csv]
python -m pipeline.run_pipeline extract  --date YYYYMMDD [--limit N]
python -m pipeline.run_pipeline backfill --start YYYYMMDD --end YYYYMMDD [--skip-extract]
python -m pipeline.run_pipeline model    --asof YYYYMMDD
python -m pipeline.run_pipeline report   --month YYYYMM
python -m pipeline.run_pipeline eda      --start YYYYMMDD --end YYYYMMDD [--out ./eda_out]

공통 옵션: --verbose, --dry-run
"""
import argparse

from . import build_dataset, collect_metrics, config, extract_attributes, interpret, monthly_report, \
    sample_data, storage, text_features, train_model
from .utils.date_utils import add_days, daterange
from .utils.io_utils import read_csv_records
from .utils.logging_utils import get_logger, setup_logging, timed
from .utils.validators import validate_date, validate_month

log = get_logger("pipeline")


def cmd_sample(a):
    n = sample_data.generate(validate_date(a.start), validate_date(a.end), per_day=a.per_day)
    log.info("가상 데이터 %d건 생성", n)


def cmd_collect(a):
    validate_date(a.date)
    if a.articles:
        storage.write_json(config.PATH_ARTICLES.format(date=a.date), read_csv_records(a.articles))
    if a.site:
        n = collect_metrics.collect(collect_metrics.CsvMetricsSource(a.site, a.portal), a.date)
        log.info("metrics: %d건", n)
    if not a.dry_run:
        build_dataset.build(a.date)


def cmd_extract(a):
    validate_date(a.date)
    if a.dry_run:
        log.info("[dry-run] 속성 추출 생략: %s", a.date)
        return
    extract_attributes.run(a.date, limit=a.limit)


def cmd_backfill(a):
    for d in daterange(validate_date(a.start), validate_date(a.end)):
        with timed(f"backfill {d}", log):
            build_dataset.build(d)
            if not a.skip_extract and not a.dry_run:
                extract_attributes.run(d)


def _window(asof: str, days: int):
    start = add_days(asof, -max(days, 1) + 1)
    df = build_dataset.load_dataset(daterange(start, asof))
    return text_features.basic_features(df) if not df.empty else df


def cmd_model(a):
    asof = validate_date(a.asof)
    df = _window(asof, config.TRAIN_DAYS)
    if df.empty:
        log.error("학습 데이터가 없습니다.")
        return
    out = {"asof": asof, "metrics": {}, "importance": {}, "effects": {}, "summary": {}, "models": {}}
    for target in ("pv", "stay_sec", "portal_inflow"):
        if target not in df:
            continue
        with timed(f"학습 {target}", log):
            model, metrics = train_model.train(df, target)
        out["metrics"][target] = metrics
        out["importance"][target] = train_model.feature_importance(model)[:20]
        out["models"][target] = model.model_to_string()

    recent = _window(asof, config.INTERP_DAYS or config.TRAIN_DAYS)
    for target in ("pv", "stay_sec"):
        if target in recent:
            fit = interpret.fit_effects(recent, target)
            out["effects"][target] = fit["effects"]
            out["summary"][target] = interpret.summary_text(fit, config.TARGETS[target])
    if a.dry_run:
        log.info("[dry-run] 저장 생략: %s", {t: m.get("r2") for t, m in out["metrics"].items()})
        return
    storage.write_json(config.PATH_MODEL.format(date=asof), out)


def cmd_report(a):
    p = monthly_report.build(validate_month(a.month))
    log.info("%s %s", p["month"], p["kpi"])


def cmd_eda(a):
    from .eda import report
    report.run(validate_date(a.start), validate_date(a.end), a.out)


def build_parser():
    ap = argparse.ArgumentParser(prog="pipeline")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sample"); s.add_argument("--start", required=True); s.add_argument("--end", required=True)
    s.add_argument("--per-day", type=int, default=50)
    c = sub.add_parser("collect"); c.add_argument("--date", required=True); c.add_argument("--articles")
    c.add_argument("--site"); c.add_argument("--portal")
    e = sub.add_parser("extract"); e.add_argument("--date", required=True); e.add_argument("--limit", type=int)
    b = sub.add_parser("backfill"); b.add_argument("--start", required=True); b.add_argument("--end", required=True)
    b.add_argument("--skip-extract", action="store_true")
    m = sub.add_parser("model"); m.add_argument("--asof", required=True)
    r = sub.add_parser("report"); r.add_argument("--month", required=True)
    x = sub.add_parser("eda"); x.add_argument("--start", required=True); x.add_argument("--end", required=True)
    x.add_argument("--out", default="./eda_out")
    return ap


COMMANDS = {"sample": cmd_sample, "collect": cmd_collect, "extract": cmd_extract, "backfill": cmd_backfill,
            "model": cmd_model, "report": cmd_report, "eda": cmd_eda}


def main(argv=None):
    a = build_parser().parse_args(argv)
    setup_logging("DEBUG" if a.verbose else config.LOG_LEVEL)
    COMMANDS[a.cmd](a)


if __name__ == "__main__":
    main()
