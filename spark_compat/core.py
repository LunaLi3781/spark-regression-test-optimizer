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
    for key in ("format", "case_fingerprint", "profile", "row_limit"):
        if left[key] != right[key]:
            raise ValueError("Incompatible run metadata: " + key)
    def index(run):
        rows = run["cases"]
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
                       "interpretation": "needs_review" if changes else "no_observed_difference"})
    return {"source_version": left["spark_version"], "target_version": right["spark_version"],
            "profile": left["profile"], "cases": output,
            "changed": sum(bool(r["changes"]) for r in output)}
