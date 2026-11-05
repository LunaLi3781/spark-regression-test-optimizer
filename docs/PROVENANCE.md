# Provenance

- Created from scratch with AI assistance for this project on 2026-11-04.
- The previous conversation described a starter ZIP at a historical sandbox path.
  No accessible ZIP or attachment was found in the chat or local Documents,
  Downloads and Desktop searches. Its source and tests were not inspected.
- All implementation and smoke tests were newly written here; no Apache Spark
  source files were copied. PySpark is an optional external dependency.
- Example features and outcomes are fictional, manually authored fixtures.
- No Amazon/AWS/Oracle private repositories, internal test names, logs, credentials,
  customer data or company documents were accessed or used for this deliverable.
- Public references: https://spark.apache.org/contributing.html and
  https://spark.apache.org/docs/latest/api/python/development/testing.html .

For future data, record public URL, revision, retrieval date, license, generation
procedure and any transformations. Do not include employer-owned material without
explicit authorization. This provenance record describes the inputs used here;
it is not a legal determination of ownership of future contributions.

## Public historical defect fixture

SPARK-52788 independently reproduced using new sample data and a Python harness.
Public issue description and fix were consulted; no upstream source file or test
was copied into this MIT repository. Upstream fix authors retain credit.
- https://issues.apache.org/jira/browse/SPARK-52788
- https://github.com/apache/spark/pull/51610
- https://spark.apache.org/releases/spark-release-4-0-1.html

The issue affects 4.0.0 and is fixed in 4.0.1. This is a historical defect
reproduction, not a claim that we discovered or fixed it, nor proof of regression
from 3.5.3 (built-in XML support differs across versions).
