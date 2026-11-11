"""Stable value encoding and conservative cross-version comparison."""
import datetime
import decimal
import hashlib
import json
import math


def canonical(value):
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return {"float": repr(value) if not math.isnan(value) else "nan"}
    if isinstance(value, decimal.Decimal):
        return {"decimal": str(value)}
    if isinstance(value, (datetime.datetime, datetime.date)):
        return {type(value).__name__: value.isoformat()}
    if isinstance(value, (bytes, bytearray)):
        return {"binary": bytes(value).hex()}
    if isinstance(value, dict):
        pairs = [[canonical(k), canonical(v)] for k, v in value.items()]
        return {"map": sorted(pairs, key=dumps)}
    if isinstance(value, (tuple, list)):
        return [canonical(v) for v in value]
    raise TypeError("Unsupported collected value type: " + type(value).__name__)


def dumps(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def fingerprint(cases):
    return hashlib.sha256(dumps(cases).encode()).hexdigest()


def compare(left, right):
    if left.get("format") != right.get("format"):
        raise ValueError("Incompatible run formats")
    if left.get("format") not in (1, 2):
        raise ValueError("Unsupported run format")
    if left["format"] == 2:
        for key in ("suite", "host_timezone", "expected_case_ids"):
            if left[key] != right[key]:
                raise ValueError("Incompatible run metadata: " + key)
        for run in (left, right):
            if (not run["expected_case_ids"] or
                    set(run["expected_case_ids"]) != {c["id"] for c in run["cases"]}):
                raise ValueError("Incomplete run")
        if left["config"]["spark.sql.session.timeZone"] != right["config"]["spark.sql.session.timeZone"]:
            raise ValueError("Different session timezones")
        if left["profile"] == "ansi-off" and any(
                run["config"]["spark.sql.ansi.enabled"] != "false" for run in (left, right)):
            raise ValueError("Controlled ANSI configuration was not applied")
    for key in ("format", "case_fingerprint", "profile", "row_limit"):
        if left[key] != right[key]:
            raise ValueError("Incompatible run metadata: " + key)
    def index(run):
        rows = run["cases"]
        if not rows:
            raise ValueError("Empty run")
        if any(r["status"] not in ("ok", "error", "inconclusive") for r in rows):
            raise ValueError("Invalid observation status")
        result = {r["id"]: r for r in rows}
        if len(result) != len(rows):
            raise ValueError("Duplicate case IDs")
        return result
    a, b = index(left), index(right)
    if a.keys() != b.keys():
        raise ValueError("Case sets differ; incomplete comparison")
    output = []
    for key in a:
        x, y = a[key], b[key]
        if x["status"] == "inconclusive" or y["status"] == "inconclusive":
            changes = ["inconclusive"]
        elif x["status"] != y["status"]:
            changes = ["outcome"]
        elif x["status"] == "error":
            changes = ["error"] if x["error"] != y["error"] else []
        else:
            changes = [field for field in ("schema", "rows") if x[field] != y[field]]
        output.append({"id": key, "changes": changes, "reference": x.get("reference"),
                       "source_status": x["status"], "target_status": y["status"],
                       "source_oracle": x.get("oracle_result"),
                       "target_oracle": y.get("oracle_result"),
                       "interpretation": "needs_review" if changes else "no_observed_difference"})
    return {"source_version": left["spark_version"], "target_version": right["spark_version"],
            "profile": left["profile"], "cases": output,
            "changed": sum(bool(r["changes"]) for r in output)}


def markdown(report):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["# Spark compatibility report", "",
             f"{report['source_version']} → {report['target_version']} ({report['profile']})",
             "", f"Cases: {len(report['cases'])}; differences/inconclusive: {report['changed']}.",
             "", "Differences require review; they are not automatically new bugs.", "",
             "| Case | Difference | Source → target | Correctness oracle |",
             "|---|---|---|---|"]
    for row in report["cases"]:
        values = [row["id"], ", ".join(row["changes"]) or "none",
                  row["source_status"] + " → " + row["target_status"],
                  str(row["source_oracle"] or "n/a") + " → " + str(row["target_oracle"] or "n/a")]
        lines.append("| " + " | ".join(cell(v) for v in values) + " |")
    return "\n".join(lines) + "\n"
