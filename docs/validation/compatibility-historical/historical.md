# Spark compatibility report

4.0.0 → 4.0.1 (defaults)

Cases: 2; differences/inconclusive: 1.

Differences require review; they are not automatically new bugs.

| Case | Difference | Source → target | Correctness oracle |
|---|---|---|---|
| xml_string_control | none | ok → ok | pass → pass |
| xml_binary_52788 | outcome | error → ok | fail → pass |
