# Spark compatibility report

4.0.0 → 4.0.1 (defaults)

Cases: 6; differences/inconclusive: 3.

Differences require review; they are not automatically new bugs.

| Case | Difference | Source → target | Correctness oracle |
|---|---|---|---|
| xml_string_control | none | ok → ok | pass → pass |
| xml_binary_52788 | outcome | error → ok | fail → pass |
| json_float_control | none | ok → ok | pass → pass |
| json_variant_52153 | rows | ok → ok | fail → pass |
| cube_union_control | none | ok → ok | pass → pass |
| cube_having_53094 | rows | ok → ok | fail → pass |
