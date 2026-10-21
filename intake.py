"""Public-only intake and offline reproducibility checks; Python standard library."""
import argparse
import csv
import hashlib
import io
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

from casebook import ROOT, load_catalog, mechanism_replay, source_events, validate_catalog

DATA = ROOT / "data"
ALLOWED_HOSTS = {"www.justice.gov", "archives.fbi.gov", "www.fbi.gov", "www.ftc.gov",
                 "www.nycourts.gov", "api.usaspending.gov"}
MAX_BYTES = 20 * 1024 * 1024
SPENDING_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"


def encode(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_url(url):
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS or parts.username or parts.password or parts.port not in (None, 443):
        raise ValueError("Only explicitly allowlisted HTTPS government sources are supported")


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url, payload=None, opener=None):
    check_url(url)
    headers = {"User-Agent": "FraudPublicResearch/0.2 (public records; no authentication)",
               "Accept": "application/json, text/html, application/pdf"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=encode(payload) if payload is not None else None, headers=headers)
    open_request = opener or urllib.request.build_opener(PublicRedirect()).open
    for attempt in range(3):
        try:
            with open_request(req, timeout=30) as response:
                check_url(response.geturl())
                content = response.read(MAX_BYTES + 1)
                if len(content) > MAX_BYTES:
                    raise ValueError("Download exceeded 20 MiB; no partial artifact accepted")
                content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
                validate_payload(content, content_type)
                return content, content_type, response.geturl()
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
            time.sleep(attempt + 1)


def validate_payload(content, content_type):
    if not content:
        raise ValueError("Empty response")
    lower = content[:200000].lower()
    if any(marker in lower for marker in (b"triggerinterstitialchallenge", b"doj-interstitial", b"access denied", b"verify you are human", b"captcha")):
        raise ValueError("Access challenge detected; not source evidence")
    if content_type == "application/pdf":
        if not content.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF signature")
    elif content_type in ("application/json", "application/geo+json"):
        json.loads(content)
    elif content_type == "text/html":
        if len(content) < 1000 or not any(t in lower for t in (b"<html", b"<!doctype html")):
            raise ValueError("Invalid or unexpectedly small HTML response")
    else:
        raise ValueError(f"Unsupported response content type: {content_type}")


def write_artifact(content, content_type):
    suffix = {"application/pdf": ".pdf", "text/html": ".html", "application/json": ".json"}.get(content_type, ".bin")
    path = DATA / "raw" / (sha(content) + suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError("Existing content-addressed artifact has unexpected bytes")
    else:
        path.write_bytes(content)
    return path.relative_to(ROOT).as_posix()


def log_attempt(record):
    DATA.mkdir(exist_ok=True)
    record = dict(record, retrieved_at=datetime.now(timezone.utc).isoformat())
    with (DATA / "intake_log.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def derived_files():
    evidence, replay = [], []
    for case in load_catalog()["cases"]:
        for event in source_events(case):
            evidence.append(dict(event, case_id=case["id"], extraction_method="human-curated factual paraphrase from publicly browsed official source; not raw source text",
                                 reviewed_on=load_catalog()["reviewed_on"]))
        if case["kind"] == "historical":
            replay.extend(mechanism_replay(case["id"], 3)["observations"])
    lines = lambda rows: b"".join((json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8") for r in rows)
    return {"evidence.jsonl": lines(evidence), "synthetic_replays.jsonl": lines(replay)}


def build():
    validate_catalog()
    files = derived_files()
    for name, content in files.items():
        (DATA / name).write_bytes(content)
    manifest = {"schema_version": 1, "catalog_sha256": sha((DATA / "cases.json").read_bytes()),
                "artifacts": {name: sha(content) for name, content in files.items()},
                "source_scope": "Curated public-source facts; generated synthetic observations kept separate; raw downloads tracked separately"}
    (DATA / "build_manifest.json").write_bytes(encode(manifest))
    return validate_catalog()


def verify():
    result = validate_catalog()
    manifest = json.loads((DATA / "build_manifest.json").read_text(encoding="utf-8"))
    if manifest["catalog_sha256"] != sha((DATA / "cases.json").read_bytes()):
        raise ValueError("Catalog digest mismatch; review changes and run intake.py build")
    for name, expected in derived_files().items():
        actual = (DATA / name).read_bytes()
        if actual != expected or manifest["artifacts"].get(name) != sha(actual):
            raise ValueError(f"Derived artifact mismatch: {name}")
    log_path = DATA / "intake_log.jsonl"
    downloads = 0
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record["status"] == "downloaded":
                path = (ROOT / record["artifact"]).resolve()
                if not path.is_relative_to((DATA / "raw").resolve()):
                    raise ValueError("Artifact path escaped raw directory")
                if sha(path.read_bytes()) != record["sha256"]:
                    raise ValueError("Downloaded artifact digest mismatch")
                downloads += 1
    if (DATA / "spending" / "provenance.json").exists():
        provenance = json.loads((DATA / "spending" / "provenance.json").read_text(encoding="utf-8"))
        raw_path = (ROOT / provenance["artifact"]).resolve()
        if not raw_path.is_relative_to((DATA / "raw").resolve()):
            raise ValueError("Spending artifact path escaped raw directory")
        raw = raw_path.read_bytes()
        if sha(raw) != provenance["sha256"]:
            raise ValueError("Spending source digest mismatch")
        normalized = normalize_awards(json.loads(raw, parse_float=Decimal))
        if spending_csv(normalized) != (DATA / "spending" / "awards.csv").read_bytes():
            raise ValueError("Spending CSV cannot be reproduced from raw response")
        result["public_awards"] = len(normalized)
    return dict(result, verified_downloads=downloads)


def fetch_sources(only=None):
    failures = 0
    cases = load_catalog()["cases"]
    if only is not None:
        cases = [c for c in cases if c["id"] == only]
        if not cases:
            raise ValueError("Unknown case ID")
    for case in cases:
        source = case["source"]
        record = dict(case_id=case["id"], requested_url=source["url"], method="direct government HTTP request")
        try:
            content, kind, final_url = download(source["url"])
            artifact = write_artifact(content, kind)
            record.update(status="downloaded", artifact=artifact, sha256=sha(content), content_type=kind, final_url=final_url)
        except (OSError, ValueError) as error:
            record.update(status="unavailable", error=str(error))
            failures += 1
        log_attempt(record)
        print(case["id"] + ": " + record["status"], flush=True)
    return failures


def normalize_awards(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list) or not payload["results"]:
        raise ValueError("Expected nonempty USAspending results list")
    rows, seen = [], set()
    for row in payload["results"]:
        identifier = row.get("generated_internal_id")
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("Missing or duplicate stable award identifier")
        seen.add(identifier)
        for field in ("Award ID", "Recipient Name", "Awarding Agency"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"Missing required field {field}")
        try:
            value = Decimal(str(row["Award Amount"]))
            if not value.is_finite():
                raise ValueError("Nonfinite award amount")
            cents = value * 100
            if cents != cents.to_integral_value():
                raise ValueError("Award amount has sub-cent precision")
        except (KeyError, InvalidOperation) as error:
            raise ValueError("Invalid award amount") from error
        for field in ("Start Date", "End Date"):
            if row.get(field):
                datetime.strptime(row[field], "%Y-%m-%d")
        rows.append(dict(award_key=identifier, award_id=row["Award ID"], recipient=row["Recipient Name"],
                         total_award_obligation_cents=int(cents), currency="USD", agency=row["Awarding Agency"],
                         start_date=row.get("Start Date") or "", end_date=row.get("End Date") or "",
                         synthetic=False, fraud_label="unlabeled", source="USAspending.gov"))
    return rows


def spending_csv(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def fetch_spending(limit):
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    payload = {"filters": {"time_period": [{"start_date": "2025-01-01", "end_date": "2025-12-31"}],
                           "award_type_codes": ["A", "B", "C", "D"]},
               "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency", "Start Date", "End Date", "generated_internal_id"],
               "page": 1, "limit": limit, "sort": "Award Amount", "order": "desc", "subawards": False}
    content, kind, final_url = download(SPENDING_URL, payload)
    if kind != "application/json":
        raise ValueError("USAspending did not return JSON")
    rows = normalize_awards(json.loads(content, parse_float=Decimal))
    artifact = write_artifact(content, kind)
    provenance = dict(requested_url=SPENDING_URL, final_url=final_url, request=payload, status="downloaded",
                      artifact=artifact, sha256=sha(content), content_type=kind,
                      retrieved_at=datetime.now(timezone.utc).isoformat(), rows=len(rows),
                      interpretation="Top total award obligations among contracts matching a 2025 activity filter, not spending during 2025. Nonrepresentative unlabeled sample. No fraud inference.",
                      reuse_basis="Public federal spending data; see DATA_SOURCES.md for agency policies and third-party caveats.")
    target = DATA / "spending"
    target.mkdir(exist_ok=True)
    (target / "awards.csv").write_bytes(spending_csv(rows))
    (target / "provenance.json").write_bytes(encode(provenance))
    log_attempt(provenance)
    return dict(public_awards=len(rows), artifact=artifact)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build", help="Rebuild curated evidence and synthetic streams, offline")
    commands.add_parser("verify", help="Verify schemas, reproducibility, and artifact hashes, offline")
    fetch = commands.add_parser("sources", help="Try downloading official case documents; log blocks without bypassing them")
    fetch.add_argument("--case", help="Only this case ID; omit to fetch all 25")
    spending = commands.add_parser("spending", help="Fetch a small real, unlabeled USAspending contract sample")
    spending.add_argument("--limit", type=int, default=25)
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = build()
        elif args.command == "verify":
            result = verify()
        elif args.command == "sources":
            failures = fetch_sources(args.case)
            print(json.dumps(dict(unavailable=failures)))
            return 1 if failures else 0
        else:
            result = fetch_spending(args.limit)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, AssertionError) as error:
        print(f"Intake failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
