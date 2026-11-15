# Boundary-case audit (2026-11-14)

32 deterministic cases exercise CUBE/HAVING (empty input, NULL keys and amounts,
duplicates, cancellation, COUNT(*) vs COUNT(column)) and JSON variant serialization
(objects/arrays with NaN, infinities, fractions, negative zero and NULL).

Expected aggregates are computed independently in Python. A grouping marker
distinguishes a real NULL key from the grand total. JSON validation rejects
nonstandard numeric constants; it does not distinguish positive and negative zero.
These are small targeted probes, not random fuzzing or a general compatibility proof.

## Measured local results

| Spark | Observations | Correctness checks passed | Failed checks |
|---|---:|---:|---:|
| 4.0.0 | 32 | 21 | 11 |
| 4.0.1 | 32 | 30 | 2 |
| 4.0.5 | 32 | 30 | 2 |

96 queries executed in separate JVMs on the same local machine with Python 3.9,
Java 17, and UTC Python/Spark timezones. [Raw runs and audits](validation/compatibility-boundary/).
Nine failures disappear between 4.0.0 and 4.0.1, consistent with the previously
validated CUBE/HAVING and JSON repairs. They are nine cases, not nine distinct bugs.

Both later versions produce identical results across this suite, yet the independent
checks reject two empty-input CUBE cases. This demonstrates why version differences
alone are insufficient to establish correctness.

## Candidate needing upstream validation

This newly authored probe still returns zero rows in all three tested versions:

```sql
SELECT region, SUM(amount) AS total, grouping(region) AS gid
FROM (
  SELECT CAST(NULL AS STRING) AS region, CAST(NULL AS INT) AS amount WHERE false
) src
GROUP BY CUBE(region)
HAVING count(*) > -1;
```

The expected global row under the grouping-set equivalence is `(NULL, NULL, 1)`;
the keyed grouping contributes no rows. COUNT(region) > -1 behaves similarly.
The oracle rationale follows the documented equivalence of CUBE to grouping sets,
including the empty grouping set/global aggregation:
https://spark.apache.org/docs/4.0.1/sql-ref-syntax-qry-select-groupby.html

Related prior issue: [SPARK-57775 / PR 56891](https://github.com/apache/spark/pull/56891).
Its description limits the lowering fix to a *single* empty grouping set, including
CUBE() without dimensions. Our probe uses CUBE(region), which includes both a keyed
and an empty grouping set. This scope distinction needs maintainer confirmation.
No claim of novelty, current-master reproduction, or new upstream fix is made.
No duplicate JIRA or PR was opened. Next: verify current source and latest feature
release, minimize against a UNION ALL/global-aggregate control, then finish duplicate
research before reporting or implementing a fix.

## Using the audit

```sh
spark-compat collect --suite boundary --output results/boundary.json
spark-compat audit results/boundary.json --output results/audit.json
```

`audit` returns exit status 1 if any oracle fails or a result is inconclusive, after
writing the report. A failed audit is a finding to investigate, not a claim that
Spark crashed. Missing or duplicate observations and mismatched suite definitions
are rejected. Comparison reports now flag equal-but-wrong results as correctness
failures even when their difference count is zero.

54 unit tests passed. This boundary expansion is locally verified; the previous
six-case historical suite also passed cloud CI in
[run 43139141286](https://github.com/LunaLi3781/spark-regression-test-optimizer/actions/runs/43139141286).
That cloud result is not evidence of a cloud run of these new 32 boundary cases.
