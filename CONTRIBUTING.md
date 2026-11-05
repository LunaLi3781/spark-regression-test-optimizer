# Contributing

Use original contributions or appropriately licensed public material. Do not
submit employer-internal code, logs, metrics, test fixtures or customer data.
Record the source and license of any imported public fixture. Keep synthetic and
measured results explicitly separated.

For a change, explain the problem and expected behavior, add focused tests, then run:

```bash
python3 -m unittest discover -s tests -v
python3 -m scripts.evaluate_demo
```

Document scoring changes and repeat the same budget/seed protocol. Do not tune on
held-out outcomes. Contributions to this repository are under its MIT license.
Contributions submitted directly to Apache Spark follow Apache's own contribution
and licensing rules instead.
