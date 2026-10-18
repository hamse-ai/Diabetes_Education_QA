"""Create a non-authoritative review-priority triage of MedQuAD candidate rows."""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/review/medquad_review_queue.csv"
OUTPUT = ROOT / "data/review/medquad_triage.csv"
RULES = [
    ("mentions_pregnancy", re.compile(r"pregnan|gestation|maternal|fetal", re.I)),
    ("mentions_youth", re.compile(r"child|children|pediatric|infant|newborn|adolescent|young adult", re.I)),
    ("population_specific_us_context", re.compile(r"american indian|native american|tribe|tribal", re.I)),
    ("individualized_dosing_language", re.compile(r"insulin dose|dosage|how much insulin|adjust.*dose|change.*dose", re.I)),
    ("research_may_be_outdated", re.compile(r"clinical trial|research (is|are) being done", re.I)),
    ("location_or_context_specific_detail", re.compile(r"medicare|medicaid|insurance|financial help|call 911|911", re.I)),
]
RARE_FOCUS = re.compile(
    r"alaninuria|mitochondrial dna|epiphyseal dysplasia|"
    r"muscular atrophy ataxia retinitis pigmentosa|rare disease",
    re.I,
)


def triage(row: dict[str, str]) -> tuple[str, str]:
    focus = row.get("focus", "")
    text = " ".join((focus, row.get("question", ""), row.get("answer", "")))
    flags = [name for name, pattern in RULES if pattern.search(text)]
    rare = row.get("source_collection") == "2_GARD_QA" or bool(RARE_FOCUS.search(focus))
    if rare:
        flags.append("rare_or_syndromic_focus")
    if rare or "american indian" in focus.lower() or "diabetes insipidus" in focus.lower():
        bucket = "likely_out_of_scope_review"
    elif flags:
        bucket = "priority_human_review"
    else:
        bucket = "general_candidate_needs_source_review"
    return bucket, ";".join(flags) if flags else "none"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"No rows found in {args.input}")
    fields = list(rows[0]) + ["triage_bucket", "triage_flags"]
    counts: Counter[str] = Counter()
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            bucket, flags = triage(row)
            counts[bucket] += 1
            writer.writerow({**row, "triage_bucket": bucket, "triage_flags": flags})
    print(f"Wrote {len(rows)} rows to {args.output}")
    print(dict(counts))
    print("Flags are screening cues only; no row is approved by this script.")


if __name__ == "__main__":
    main()
