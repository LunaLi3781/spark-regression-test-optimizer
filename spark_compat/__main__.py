"""Run in separate Python environments, then compare JSON artifacts offline."""
import argparse
import json
import platform
import os
import time
from pathlib import Path

from .cases import SUITES
from .oracles import check
from .core import canonical, compare, dumps, fingerprint, markdown


def collect(profile, limit, suite="smoke"):
    cases = SUITES[suite]
    # PySpark converts collected timestamps using the Python process timezone.
    if not hasattr(time, "tzset"):
        raise RuntimeError("Collector currently requires a Unix host with time.tzset")
    os.environ["TZ"] = "UTC"
    time.tzset()
    from pyspark.sql import SparkSession
    spark = (SparkSession.builder.master("local[2]").appName("spark-compat")
             .config("spark.ui.enabled", "false").config("spark.sql.session.timeZone", "UTC")
             .config("spark.sql.shuffle.partitions", "2").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    results = []
    try:
        if profile == "ansi-off":
            spark.conf.set("spark.sql.ansi.enabled", "false")
        if suite == "historical":
            spark.conf.set("spark.sql.binaryOutputStyle", "UTF-8")
        config = {k: spark.conf.get(k) for k in
                  ("spark.sql.ansi.enabled", "spark.sql.session.timeZone")}
        if suite == "historical":
            config["spark.sql.binaryOutputStyle"] = spark.conf.get("spark.sql.binaryOutputStyle")
        for case in cases:
            record = dict(case)
            try:
                frame = spark.sql(case["sql"])
                rows = frame.limit(limit + 1).collect()
                if len(rows) > limit:
                    record.update(status="inconclusive", reason="row_limit_exceeded")
                else:
                    record.update(status="ok", schema=frame.schema.jsonValue(),
                                  rows=sorted([canonical(row) for row in rows], key=dumps))
                    if case.get("oracle"):
                        record["oracle_result"] = "pass" if check(case, rows) else "fail"
            except Exception as exc:
                get_class = getattr(exc, "getErrorClass", lambda: None)
                condition = get_class()
                if (case["id"] == "xml_binary_52788" and
                        "Failed to convert value" in str(exc) and
                        "BinaryType" in str(exc) and "XML" in str(exc)):
                    condition = "SPARK-52788_BINARY_XML_CONVERSION"
                if not condition:
                    raise RuntimeError("Unclassified execution failure in " + case["id"]) from exc
                record.update(status="error", error=condition)
                if case.get("oracle"):
                    record["oracle_result"] = "fail"
            results.append(record)
        return {"format": 2, "suite": suite, "host_timezone": "UTC",
                "expected_case_ids": [c["id"] for c in cases], "spark_version": spark.version, "python": platform.python_version(),
                "java": spark.sparkContext._jvm.java.lang.System.getProperty("java.version"),
                "profile": profile, "config": config, "row_limit": limit,
                "case_fingerprint": fingerprint(cases), "cases": results}
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
    run.add_argument("--suite", choices=sorted(SUITES), default="smoke")
    run.add_argument("--profile", choices=["defaults", "ansi-off"], default="defaults")
    run.add_argument("--row-limit", type=int, default=1000)
    run.add_argument("--output", required=True)
    diff = sub.add_parser("compare")
    diff.add_argument("source")
    diff.add_argument("target")
    diff.add_argument("--output", required=True)
    diff.add_argument("--markdown")
    args = parser.parse_args()
    if args.command == "collect":
        if args.row_limit < 1:
            parser.error("--row-limit must be positive")
        report = collect(args.profile, args.row_limit, args.suite)
    else:
        report = compare(json.loads(Path(args.source).read_text()),
                         json.loads(Path(args.target).read_text()))
    write(args.output, report)
    if args.command == "compare" and args.markdown:
        path = Path(args.markdown)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown(report), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
