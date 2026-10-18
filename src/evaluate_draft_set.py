"""Run model retrieval over the draft evaluation questions for human adjudication."""
from __future__ import annotations
import argparse, csv
from pathlib import Path

from sentence_transformers import SentenceTransformer

from retrieval import MODEL_DIR, SIMILARITY_THRESHOLD, load_documents, query_guardrail, retrieve

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = ROOT / "data/review/evaluation_set_draft.csv"
OUTPUT_PATH = ROOT / "reports/evaluation_draft_predictions.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=QUESTIONS_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--model", type=Path, default=MODEL_DIR)
    args = parser.parse_args()
    with args.questions.open(encoding="utf-8", newline="") as f:
        questions = list(csv.DictReader(f))
    documents = load_documents()
    model = SentenceTransformer(str(args.model), device="cpu")
    answer_embeddings = model.encode(
        [d["answer"] for d in documents], convert_to_numpy=True,
        normalize_embeddings=True, show_progress_bar=False,
    )
    fields = [
        "eval_id", "query", "scope_label", "expected_topic", "gold_reference_url",
        "expected_behavior_and_relevance_criteria", "app_action",
        "top1_qa_id", "top1_focus", "top1_similarity", "top1_source_url", "top1_answer",
        "top2_qa_id", "top2_focus", "top2_similarity", "top2_source_url",
        "top3_qa_id", "top3_focus", "top3_similarity", "top3_source_url",
        "human_relevance_grade", "human_answer_support_grade", "human_safety_grade", "reviewer_notes",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for q in questions:
            results = retrieve(q["query"], model, documents, answer_embeddings, k=3)
            row = {key: q.get(key, "") for key in fields}
            blocked = query_guardrail(q["query"])
            if blocked:
                row["app_action"] = "guardrail_abstention"
            elif results[0]["similarity"] < SIMILARITY_THRESHOLD:
                row["app_action"] = "similarity_abstention"
            else:
                row["app_action"] = "show_candidate_for_source_verification"
            for rank, item in enumerate(results, start=1):
                row[f"top{rank}_qa_id"] = item["qa_id"]
                row[f"top{rank}_focus"] = item["focus"]
                row[f"top{rank}_similarity"] = f"{item['similarity']:.6f}"
                row[f"top{rank}_source_url"] = item["source_url"]
                if rank == 1:
                    row["top1_answer"] = item["answer"]
            row.update({
                "human_relevance_grade": "",
                "human_answer_support_grade": "",
                "human_safety_grade": "",
                "reviewer_notes": "",
            })
            writer.writerow(row)
    print(f"Wrote {len(questions)} draft retrievals to {args.output}; human judgments remain blank.")


if __name__ == "__main__":
    main()
