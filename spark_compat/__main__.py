"""Run in separate Python environments, then compare JSON artifacts offline."""
import argparse
import json
import platform
from pathlib import Path

from .cases import CASES
from .core import canonical, compare, dumps, fingerprint


def collect(profile, limit):
    from pyspark.sql import SparkSession
    spark = (SparkSession.builder.master("local[2]").appName("spark-compat")
             .config("spark.ui.enabled", "false").config("spark.sql.session.timeZone", "UTC")
             .config("spark.sql.shuffle.partitions", "2").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    results = []
    try:
        if profile == "ansi-off":
            spark.conf.set("spark.sql.ansi.enabled", "false")
        config = {k: spark.conf.get(k) for k in
                  ("spark.sql.ansi.enabled", "spark.sql.session.timeZone")}
        for case in CASES:
            record = dict(case)
            try:
                frame = spark.sql(case["sql"])
                rows = frame.limit(limit + 1).collect()
                if len(rows) > limit:
                    record.update(status="inconclusive", reason="row_limit_exceeded")
                else:
                    record.update(status="ok", schema=frame.schema.jsonValue(),
                                  rows=sorted([canonical(row) for row in rows], key=dumps))
            except Exception as exc:
                get_class = getattr(exc, "getErrorClass", lambda: None)
                condition = get_class()
                if not condition:
                    raise RuntimeError("Unclassified execution failure in " + case["id"]) from exc
                record.update(status="error", error=condition)
            results.append(record)
        return {"format": 1, "spark_version": spark.version, "python": platform.python_version(),
                "java": spark.sparkContext._jvm.java.lang.System.getProperty("java.version"),
                "profile": profile, "config": config, "row_limit": limit,
                "case_fingerprint": fingerprint(CASES), "cases": results}
    finally:
        spark.stop()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("collect")
    run.add_argument("--profile", choices=["defaults", "ansi-off"], default="defaults")
    run.add_argument("--row-limit", type=int, default=1000)
    run.add_argument("--output", required=True)
    diff = sub.add_parser("compare")
    diff.add_argument("source")
    diff.add_argument("target")
    diff.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "collect":
        if args.row_limit < 1:
            parser.error("--row-limit must be positive")
        report = collect(args.profile, args.row_limit)
    else:
        report = compare(json.loads(Path(args.source).read_text()),
                         json.loads(Path(args.target).read_text()))
    write(args.output, report)
    print(args.output)


if __name__ == "__main__":
    main()
