"""Group MedQuAD QA rows by source page to make provenance review manageable."""
from __future__ import annotations
import argparse, csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/review/medquad_review_queue.csv"
OUTPUT = ROOT / "data/review/source_document_review.csv"
REVIEW_FIELDS = [
    "source_review_status", "current_official_url", "accessibility_review",
    "content_support_review", "currentness_review", "scope_review",
    "safety_review", "checked_on", "reviewer_notes",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    groups = defaultdict(list)
    for row in rows:
        key = (row["doc_id"], row["source_collection"], row["focus"], row["source_url"])
        groups[key].append(row)
    fields = ["doc_id", "source_collection", "focus", "source_url", "qa_count", "qa_ids", "questions"] + REVIEW_FIELDS
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for (doc_id, collection, focus, url), items in sorted(groups.items()):
            writer.writerow({
                "doc_id": doc_id,
                "source_collection": collection,
                "focus": focus,
                "source_url": url,
                "qa_count": len(items),
                "qa_ids": ";".join(r["qa_id"] for r in items),
                "questions": " | ".join(r["question"] for r in items),
                **{field: "" for field in REVIEW_FIELDS},
            })
    print(f"Grouped {len(rows)} QA rows into {len(groups)} source-page review rows: {args.output}")


if __name__ == "__main__":
    main()
