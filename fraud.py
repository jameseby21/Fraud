"""Deterministic investigation fixture and explainable screening engine. Stdlib only."""
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone

VERSION = "0.1.0"


def fixtures():
    rows = []
    origin = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def add(day, sender, recipient, cents, memo):
        rows.append(dict(id=f"TX-{len(rows)+1:04}", timestamp=(origin + timedelta(days=day)).isoformat(),
                         sender=sender, recipient=recipient, amount_cents=cents, currency="USD", memo=memo,
                         source="fabricated-fixture-v1", synthetic=True))

    for day in range(30):
        add(day, f"Customer-{day % 9}", "Ordinary-Shop", 4500 + day * 113, "Retail payment")
        if day % 5 == 0:
            add(day, "Ordinary-Shop", "Wholesaler", 12000, "Inventory")
    # Investment-like inflows followed by payouts: suspicion, not proof of a Ponzi scheme.
    for day in range(4):
        add(day, f"Investor-{day}", "Orion-Fund", 500000, "Subscription")
    for day in range(4, 8):
        add(day, "Orion-Fund", f"Investor-{day-4}", 400000, "Distribution")
    # Two directed cycles, plus a benign circular settlement lookalike.
    for offset in (10, 15):
        for i, (a, b) in enumerate((("Aster-A", "Aster-B"), ("Aster-B", "Aster-C"), ("Aster-C", "Aster-A"))):
            add(offset + i / 24, a, b, 200000 - i * 1000, "Consulting")
    for i, (a, b) in enumerate((("Settlement-A", "Settlement-B"), ("Settlement-B", "Settlement-C"), ("Settlement-C", "Settlement-A"))):
        add(20 + i / 24, a, b, 100000, "Documented settlement")
    truth = {"Orion-Fund": "fabricated suspicious investment pattern",
             "Aster-A": "fabricated suspicious circular flow",
             "Aster-B": "fabricated suspicious circular flow",
             "Aster-C": "fabricated suspicious circular flow"}
    return rows, truth


def analyze(rows):
    """Rules consume transactions only; the answer key is deliberately separate."""
    inbound, outbound = defaultdict(list), defaultdict(list)
    for row in rows:
        inbound[row["recipient"]].append(row)
        outbound[row["sender"]].append(row)
    alerts = []
    for entity in sorted(set(inbound) | set(outbound)):
        ins, outs = inbound[entity], outbound[entity]
        incoming = sum(r["amount_cents"] for r in ins)
        returning = [r for r in outs if r["recipient"] in {x["sender"] for x in ins}]
        ratio = sum(r["amount_cents"] for r in returning) / incoming if incoming else 0
        if len({r["sender"] for r in ins}) >= 4 and ratio >= .7:
            evidence = sorted(ins + returning, key=lambda r: r["id"])
            alerts.append(dict(entity=entity, rule="RETURN-TO-CONTRIBUTORS", priority=80,
                               explanation=f"{ratio:.0%} of incoming value paid to prior contributors; inspect economic purpose and independent earnings.",
                               alternative="Legitimate redemptions or distributions can produce this pattern.",
                               evidence_ids=[r["id"] for r in evidence]))
        cycles = set()
        for first in outs:
            for second in outbound[first["recipient"]]:
                if second["recipient"] in (entity, first["recipient"]):
                    continue
                for third in outbound[second["recipient"]]:
                    times = [datetime.fromisoformat(r["timestamp"]) for r in (first, second, third)]
                    amounts = [r["amount_cents"] for r in (first, second, third)]
                    if third["recipient"] == entity and times[0] <= times[1] <= times[2] and (times[2]-times[0]).total_seconds() <= 86400 and min(amounts) >= .95 * max(amounts):
                        cycles.update(r["id"] for r in (first, second, third))
        if cycles:
            alerts.append(dict(entity=entity, rule="THREE-PARTY-CYCLE", priority=65,
                               explanation="Similar amounts returned through three accounts within 24 hours.",
                               alternative="Treasury operations and documented settlements can be legitimate.",
                               evidence_ids=sorted(cycles)))
    return sorted(alerts, key=lambda a: (-a["priority"], a["entity"]))


def report():
    rows, truth = fixtures()
    alerts = analyze(rows)
    flagged = {a["entity"] for a in alerts}
    entities = {r[k] for r in rows for k in ("sender", "recipient")}
    positives = set(truth)
    tp, fp, fn = len(flagged & positives), len(flagged - positives), len(positives - flagged)
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return dict(synthetic=True, engine_version=VERSION, fixture_sha256=digest, transactions=rows, alerts=alerts,
                evaluation=dict(unit="entity", true_positives=tp, false_positives=fp, false_negatives=fn,
                                true_negatives=len(entities - flagged - positives),
                                precision=tp / len(flagged) if flagged else None,
                                recall=tp / len(positives) if positives else None), answer_key=truth,
                limitations="Fixture performance is not evidence of real-world accuracy. Priorities are rule-based rankings, not fraud probabilities.")
