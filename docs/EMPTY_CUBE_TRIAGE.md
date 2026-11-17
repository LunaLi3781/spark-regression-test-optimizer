# Empty mixed grouping sets: upstream triage

Validated 2026-11-16 with original synthetic, AI-assisted queries. No employer inputs.

## Minimal reproduction

```sql
SELECT region, SUM(amount) AS total, grouping(region) AS gid
FROM (
  SELECT CAST(NULL AS STRING) AS region, CAST(NULL AS INT) AS amount WHERE false
) src
GROUP BY CUBE(region);
```

Expected from grouping-set/global-aggregate equivalence: `(NULL, NULL, 1)`.
Observed: zero rows. ROLLUP(region), GROUPING SETS ((region), ()), and CUBE with
HAVING count(*) > -1 exhibit the same discrepancy.

| Environment | Three controls | Empty mixed grouping sets |
|---|---|---|
| 4.0.5, Python 3.9 / Java 17, local | pass | zero rows |
| 4.3.0, Python 3.11 / Java 21, CI | pass | zero rows |
| 5.0.0-SNAPSHOT, Python 3.11 / Java 21, source CI | pass | zero rows |

Controls verify a global aggregate emits its NULL total, an empty keyed aggregate
emits no rows, and nonempty CUBE produces both keyed and total rows.
On 4.3.0 and master, the single GROUPING SETS (()) returns one row, unlike mixed sets.

Master SHA: `3438c728d38c11fc173f0829b86709c639123961`.
[Successful source build and reproduction](https://github.com/LunaLi3781/spark-regression-test-optimizer/actions/runs/44032228060).
[Raw SQL, results and optimized plans](validation/empty-cube-source/).
A successful investigation job means collection and controls passed, not that the
candidate query results were correct. The mismatch is explicitly recorded.

## Related work

[SPARK-57775 / PR 56891](https://github.com/apache/spark/pull/56891) fixes only a
single empty grouping set, including CUBE()/ROLLUP() without dimensions. The current
GroupingAnalyticsTransformer source explicitly retains that restriction. This
probe includes both a keyed and an empty grouping set. Public PR/JIRA searches found
related work but did not establish a separate duplicate for this scope; this is
not an exhaustive novelty claim.

The expectation follows Spark's documented equivalence of grouping sets to UNION ALL
of the corresponding aggregates:
https://spark.apache.org/docs/4.0.1/sql-ref-syntax-qry-select-groupby.html

No new JIRA or upstream patch has yet been submitted for this candidate. A fix must
preserve NULL-key groups, grouping IDs, duplicate grouping sets, HAVING, empty/nonempty
input, and both analyzers. Replacing the entire plan with a global aggregate would
be incorrect for keyed sets. Scope and approach merit maintainer discussion before
a broad analyzer change.

## Independent reproduction

`python -m scripts.probe_empty_cube --output results/probe.json` executes eight
queries and checks three controls. Workflow `Empty CUBE source investigation`
runs it against 4.3.0 and pinned unmodified source. 57 unit tests pass, including
rejection of incomplete observations and failed controls.
