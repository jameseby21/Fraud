"""Public case metadata and explicitly synthetic, point-in-time mechanism labs."""
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODEL_VERSION = "mechanism-rules-1"

# Deliberately illustrative thresholds. Values below are fabricated, not estimates
# of actual losses, financial records, or historical detectability.
MODELS = {
    "balance_confirmation": ("Unconfirmed balance share", "reported_assets", "confirmed_assets", .20,
        [(100, 98), (120, 110), (160, 90)], "Independent confirmations may be incomplete or lagged."),
    "invoice_confirmation": ("Unconfirmed receivable share", "invoiced_value", "buyer_confirmed_value", .25,
        [(100, 98), (160, 150), (240, 90)], "Disputes, delivery timing, and incomplete confirmations can explain a gap."),
    "customer_asset_coverage": ("Uncovered customer liability share", "customer_liabilities", "verified_customer_assets", .10,
        [(100, 100), (180, 175), (300, 160)], "Asset valuation, settlement timing, and incomplete custody coverage need reconciliation."),
    "claim_validation": ("Unvalidated claim share", "testable_claims", "independently_validated_claims", .40,
        [(10, 10), (20, 18), (30, 8)], "Unvalidated means unverified, not false; tests may not cover equivalent conditions."),
    "earnings_cash_gap": ("Earnings not matched by operating cash share", "reported_earnings", "operating_cash", .50,
        [(100, 95), (150, 130), (220, 60)], "Growth, working capital, and lawful accounting choices can produce the same pattern."),
    "related_party_review": ("Transfer value lacking documented approval share", "reviewed_transfers", "documented_approved_transfers", .20,
        [(100, 100), (180, 170), (260, 120)], "Missing approval in a dataset does not establish unauthorized activity."),
    "period_end_gap": ("Reporting-date reduction from surrounding exposure share", "surrounding_receivable", "reporting_date_receivable", .50,
        [(100, 95), (180, 160), (300, 50)], "Legitimate settlement and seasonal activity can reduce period-end balances."),
    "recruitment_dependence": ("Rewards not covered by external sales share", "participant_rewards", "external_sales_margin", .50,
        [(100, 100), (160, 140), (250, 40)], "Subsidized growth can be legitimate; examine the actual compensation arrangement."),
    "payout_coverage": ("Distributions not covered by verified earnings share", "distributions", "verified_trading_earnings", .50,
        [(100, 100), (180, 150), (300, 60)], "Capital redemptions can be lawful and are not necessarily earnings distributions."),
    "test_realworld_gap": ("Road measurement excess relative to road value", "road_measurement", "lab_measurement", .60,
        [(100, 98), (120, 100), (500, 100)], "Laboratory and road conditions can differ without deliberate test manipulation."),
    "preannouncement_pattern": ("Share of reviewed events with profitable prior positions", "reviewed_events", "events_without_profitable_prior_positions", .70,
        [(10, 8), (20, 12), (30, 3)], "Selection bias, chance, public information, and strategy exposure can explain returns."),
    "authorization_rate": ("Product share lacking affirmative authorization", "opened_products", "independently_authorized_products", .10,
        [(100, 99), (180, 176), (300, 210)], "Incomplete consent archives, household authority, and channel migrations can create apparent gaps."),
    "monitoring_escalation": ("Flagged activity continuing after escalation", "flagged_transfers", "flagged_transfers_stopped", .40,
        [(100, 95), (180, 165), (300, 80)], "Complaint duplication, delayed investigation, and lawful transfers can affect intervention measures."),
}


def load_catalog():
    catalog = json.loads((ROOT / "data" / "cases.json").read_text(encoding="utf-8"))
    outcome_data = json.loads((ROOT / "data" / "case_outcomes.json").read_text(encoding="utf-8"))
    outcomes = {item["id"]: item for item in outcome_data["outcomes"]}
    for case in catalog["cases"]:
        if case["kind"] == "historical" and case["id"] in outcomes:
            case["resolution"] = outcomes[case["id"]]
    catalog["outcome_amount_note"] = outcome_data["amount_note"]
    return catalog


def get_case(case_id):
    for case in load_catalog()["cases"]:
        if case["id"] == case_id:
            return case
    raise KeyError(case_id)


def source_events(case):
    source = case["source"]
    # No invented publication date: unknown dates are gated conservatively at review.
    available = source["published_on"] or load_catalog()["reviewed_on"]
    disposition = case.get("resolution", {}).get("criminal_disposition")
    event_type = "public_allegation_or_research" if case["kind"] != "historical" else (
        "reported_mixed_legal_outcome" if disposition in {"acquitted", "mixed_verdict", "partial_reversal"}
        else "reported_resolved_legal_outcome")
    return [dict(id=case["id"] + "-source-1", occurred_on=case.get("outcome_on") or available,
                 available_on=available, date_basis="source publication" if source["published_on"] else "publication unknown; first catalog review used conservatively",
                 type=event_type,
                 statement=case.get("outcome") or case["summary"], source=source, synthetic=False)]


def public_replay(case_id, as_of):
    date.fromisoformat(as_of)
    case = get_case(case_id)
    events = [e for e in source_events(case) if e["available_on"] <= as_of]
    return dict(case_id=case_id, name=case["name"], as_of=as_of, mode="public-source chronology",
                events=events, outcome=case.get("outcome") if events else None,
                warning="Retrospective source chronology, not an early-detection benchmark. A source published later cannot be used at an earlier date.")


def mechanism_replay(case_id, step):
    case = get_case(case_id)
    if case["kind"] != "historical":
        raise ValueError("Modern subjects receive research questions, not fabricated incriminating observations.")
    if type(step) is not int or not 0 <= step <= 3:
        raise ValueError("step must be an integer from 0 to 3")
    title, denominator, verified, threshold, values, alternative = MODELS[case["model"]]
    observations = []
    for i, (total, confirmed) in enumerate(values[:step], 1):
        observations.append(dict(id=f"{case_id}-SIM-{i}", event_step=i, available_step=i,
                                 synthetic=True, units="fabricated normalized units; not actual amounts",
                                 features={denominator: total, verified: confirmed}))
    latest = observations[-1] if observations else None
    value = (latest["features"][denominator] - latest["features"][verified]) / latest["features"][denominator] if latest else None
    trace = dict(feature_name=title, formula=f"({denominator} - {verified}) / {denominator}",
                 operands=latest["features"] if latest else {}, value=value, comparator=">", threshold=threshold,
                 evidence_ids=[latest["id"]] if latest else [],
                 result="insufficient_data" if value is None else "review" if value > threshold else "no_rule_trigger",
                 alternative=alternative)
    digest = hashlib.sha256(json.dumps(observations, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return dict(case_id=case_id, step=step, model_version=MODEL_VERSION, synthetic=True,
                observations=observations, trace=trace, input_sha256=digest,
                warning="Synthetic mechanism exercise inspired by a documented case. None of these numeric observations are historical records. Thresholds are illustrative, not fitted. No real-world accuracy or early detection is established.")


def validate_catalog():
    catalog = load_catalog()
    cases = catalog["cases"]
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(len({c["id"] for c in cases}) == len(cases), "Duplicate case ID")
    historical = sum(c["kind"] == "historical" for c in cases)
    modern = sum(c["kind"] == "modern" for c in cases)
    require(historical >= 26 and modern == 5, "Expected at least 26 historical and exactly 5 modern cases")
    for c in cases:
        require(c["source"]["url"].startswith("https://"), "Source must use HTTPS")
        if c["source"]["published_on"]:
            date.fromisoformat(c["source"]["published_on"])
        if c["kind"] == "historical":
            require(c["model"] in MODELS and c["outcome"] and c["outcome_on"], "Historical entry needs model and sourced outcome")
            date.fromisoformat(c["outcome_on"])
            resolution = c.get("resolution")
            require(resolution and resolution["id"] == c["id"], "Historical entry needs a matching structured resolution")
            require(resolution["type"] and resolution["criminal_disposition"] and resolution["forum"], "Resolution fields cannot be empty")
            require(resolution["imprisonment_months"] is None or resolution["imprisonment_months"] > 0, "Invalid imprisonment term")
            for remedy in resolution.get("remedies", []):
                require(remedy["amount_usd"] > 0 and remedy["type"] and remedy["scope"], "Invalid remedy")
        else:
            require(c["outcome"] is None and c["outcome_on"] is None, "Modern entries cannot carry proven outcomes")
            require(all(c[k] for k in ("question", "needed_data", "method", "counterevidence", "data_gap")), "Modern entry lacks research context")
    return dict(historical=historical, modern=modern, model_families=len(MODELS), valid=True)
