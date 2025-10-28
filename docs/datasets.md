# Data contracts

FlowGuard consumes four CSV extracts in `data/`: `production.csv`, `inventory.csv`, `sales_orders.csv`, and `installations.csv`. Validation checks required columns before field-level checks. `known_issues.json` contains seeded issue keys used only for evaluating the synthetic demo.

The inputs are deliberately imperfect. Do not treat their quantities as production data or use the evaluation labels to train a business risk model.
