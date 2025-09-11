from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


REQUIRED = {
    "production": {"date", "line_id", "sku", "planned_qty", "produced_qty"},
    "inventory": {"snapshot_date", "sku", "available_qty"},
    "sales_orders": {"order_id", "order_date", "sku", "qty", "status"},
    "installations": {"install_id", "order_id", "sku", "qty", "status"},
}
FILES = {name: f"{name}.csv" for name in REQUIRED}


@dataclass
class Finding:
    issue_key: str
    rule_id: str
    dataset: str
    record_ref: str
    severity: str
    impact_score: int
    title: str
    details: str
    suggested_action: str

    def to_dict(self) -> dict:
        return asdict(self)


def _finding(
    *, key: str, rule: str, dataset: str, ref: str, severity: str,
    impact: int, title: str, details: str, action: str,
) -> Finding:
    return Finding(key, rule, dataset, ref, severity, impact, title, details, action)


def load_sources(data_dir: Path) -> dict[str, pd.DataFrame]:
    return {name: pd.read_csv(data_dir / filename) for name, filename in FILES.items()}


def validate(sources: dict[str, pd.DataFrame]) -> list[Finding]:
    findings: list[Finding] = []
    for dataset, required in REQUIRED.items():
        frame = sources[dataset]
        missing = sorted(required - set(frame.columns))
        if missing:
            findings.append(_finding(
                key=f"schema:{dataset}:{','.join(missing)}", rule="SCHEMA_DRIFT",
                dataset=dataset, ref="file", severity="critical", impact=5,
                title=f"Unexpected schema in {dataset}",
                details=f"Required columns are missing: {', '.join(missing)}.",
                action="Confirm the upstream export format and map the renamed or missing columns before rerunning.",
            ))

    # Stop field-level checks when a source's schema is incomplete.
    if any(f.rule_id == "SCHEMA_DRIFT" for f in findings):
        return findings

    orders = sources["sales_orders"]
    installations = sources["installations"]
    inventory = sources["inventory"]

    for order_id, group in orders.groupby("order_id", dropna=False):
        if len(group) > 1:
            findings.append(_finding(
                key=f"duplicate-order:{order_id}", rule="DUPLICATE_ORDER_ID",
                dataset="sales_orders", ref=str(order_id), severity="high", impact=4,
                title=f"Duplicate sales order {order_id}",
                details=f"Order ID {order_id} appears {len(group)} times in the sales export.",
                action="Check the source system for a duplicated export row. Keep one verified order before reporting totals.",
            ))

    for dataset in ("production", "inventory", "sales_orders", "installations"):
        quantity_column = "available_qty" if dataset == "inventory" else (
            "produced_qty" if dataset == "production" else "qty"
        )
        frame = sources[dataset]
        for index, row in frame.iterrows():
            value = row[quantity_column]
            if pd.isna(value) or value < 0:
                ref_col = "order_id" if "order_id" in frame.columns else "sku"
                ref = str(row[ref_col])
                findings.append(_finding(
                    key=f"invalid-quantity:{dataset}:{index}", rule="INVALID_QUANTITY",
                    dataset=dataset, ref=ref, severity="high", impact=3,
                    title=f"Invalid quantity in {dataset}",
                    details=f"{quantity_column} is {value!r}; quantities must be present and non-negative.",
                    action="Verify the source value and correct it upstream; do not substitute a guessed quantity.",
                ))

    order_ids = set(orders["order_id"].dropna().astype(str))
    for _, install in installations.iterrows():
        order_id = str(install["order_id"])
        if order_id not in order_ids:
            findings.append(_finding(
                key=f"orphan-install:{install['install_id']}", rule="MISSING_ORDER_REFERENCE",
                dataset="installations", ref=str(install["install_id"]), severity="high", impact=4,
                title=f"Installation {install['install_id']} has no matching order",
                details=f"Installation references order {order_id}, which is absent from the sales export.",
                action="Check whether the order was omitted from the sales extract or the installation has the wrong order ID.",
            ))
            continue
        matching = orders[orders["order_id"].astype(str) == order_id]
        if len(matching) != 1:
            continue
        order = matching.iloc[0]
        if str(install["sku"]) != str(order["sku"]):
            findings.append(_finding(
                key=f"sku-mismatch:{install['install_id']}", rule="CROSS_SYSTEM_SKU_MISMATCH",
                dataset="installations", ref=str(install["install_id"]), severity="high", impact=4,
                title=f"SKU mismatch for installation {install['install_id']}",
                details=f"Installation SKU {install['sku']} differs from sales order SKU {order['sku']}.",
                action="Confirm the installed product against the source order and correct the source record if needed.",
            ))

    completed = installations[installations["status"].astype(str).str.lower() == "complete"]
    for sku, group in completed.groupby("sku"):
        order_lookup = orders.drop_duplicates("order_id").set_index("order_id")["qty"].to_dict()
        exceeding = []
        for _, row in group.iterrows():
            ordered_qty = order_lookup.get(row["order_id"])
            if ordered_qty is not None and row["qty"] > ordered_qty:
                exceeding.append(f"{row['install_id']} ({row['qty']} installed vs {ordered_qty} ordered)")
        if exceeding:
            findings.append(_finding(
                key=f"install-over-order:{sku}:{','.join(sorted(r.split(' ')[0] for r in exceeding))}",
                rule="INSTALL_QTY_EXCEEDS_ORDER", dataset="installations", ref=str(sku),
                severity="critical", impact=5,
                title=f"Completed installation quantity exceeds order for {sku}",
                details="; ".join(exceeding),
                action="Pause downstream completion reporting and reconcile installation quantities with the approved order.",
            ))

    available_by_sku = inventory.groupby("sku")["available_qty"].sum().to_dict()
    installed_by_sku = completed.groupby("sku")["qty"].sum().to_dict()
    for sku, installed_qty in installed_by_sku.items():
        available_qty = available_by_sku.get(sku)
        if available_qty is not None and installed_qty > available_qty:
            findings.append(_finding(
                key=f"inventory-reconciliation:{sku}", rule="INSTALLS_EXCEED_AVAILABLE_INVENTORY",
                dataset="inventory", ref=str(sku), severity="critical", impact=5,
                title=f"Completed installations exceed available inventory for {sku}",
                details=f"Completed installations total {installed_qty} units, while the inventory snapshot shows {available_qty} available.",
                action="Check inventory timing, adjustments, and installation records before refreshing operations reporting.",
            ))

    return findings
