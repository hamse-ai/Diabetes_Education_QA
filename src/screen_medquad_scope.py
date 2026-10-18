"""Draft a scope-only screen; this does not validate clinical content."""
from __future__ import annotations
import argparse, csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/review/medquad_review_queue.csv"
OUTPUT = ROOT / "data/review/medquad_scope_screen.csv"


def decide(row: dict[str, str]) -> tuple[str, str]:
    focus = row.get("focus", "")
    source = row.get("source_collection", "")
    if source == "2_GARD_QA":
        return "exclude_pending_confirmation", "Rare-disease collection; outside basic adult diabetes education scope."
    if focus == "I Can Lower My Risk for Type 2 Diabetes: A Guide for American Indians":
        return "exclude_pending_confirmation", "Population-specific US guide; retain only if scope is deliberately broadened and content rechecked."
    if focus == "Financial Help for Diabetes Care":
        return "exclude_pending_confirmation", "Primarily US insurance/benefit guidance; not portable for a general international English audience."
    return "in_scope_pending_content_review", "Topic appears relevant to general adult diabetes education; source, currentness, safety, and answer quality remain unreviewed."


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0]) + ["scope_decision_draft", "scope_rationale"]
    counts = {}
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            decision, rationale = decide(row)
            counts[decision] = counts.get(decision, 0) + 1
            writer.writerow({**row, "scope_decision_draft": decision, "scope_rationale": rationale})
    print(f"Wrote {len(rows)} rows to {args.output}; counts={counts}")
    print("This is a scope-only draft, not content or clinical approval.")


if __name__ == "__main__":
    main()
