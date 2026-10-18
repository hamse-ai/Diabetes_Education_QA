"""Local, source-linked semantic retrieval for the Streamlit prototype."""
from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "reports/models/medquad_minilm_scope_docsplit_v002/model"
QUEUE_PATH = ROOT / "data/review/medquad_review_queue.csv"
SCOPE_PATH = ROOT / "data/review/medquad_scope_screen.csv"
SIMILARITY_THRESHOLD = 0.50

EMERGENCY_RE = re.compile(
    r"(trouble breathing|difficulty breathing|unconscious|passed out|"
    r"seizure|severe chest pain|vomit.{0,30}(deep|rapid) breath|"
    r"vomit.{0,35}(can't|cannot|unable to).{0,20}(keep|hold).{0,15}(food|fluid|drink)|"
    r"fruity breath|high ketones|severe low blood sugar|diabetic ketoacidosis|\bdka\b)", re.I,
)
PERSONAL_ACTION_RE = re.compile(
    r"(my\b.{0,40}(blood sugar|glucose|a1c|insulin|medicine|medication)|"
    r"(how much|how many units|what dose|should i|can i|do i need to).{0,50}"
    r"(insulin|medicine|medication|tablet|pill|dose)|"
    r"(stop|skip|change|increase|decrease|double|adjust).{0,30}"
    r"(insulin|medicine|medication|dose|tablet|pill)|"
    r"\bfor me\b.{0,60}(medicine|medication|treatment|insulin)|"
    r"\b( medicine| medication| insulin)\b.{0,45}\bfor me\b)", re.I,
)
PERSONAL_DIAGNOSIS_RE = re.compile(
    r"\b(do i have|could i have|am i diabetic|does this mean i have|"
    r"mean i have|how do i know if i have|can you tell me if i have)\b", re.I,
)


def load_documents() -> list[dict[str, str]]:
    with QUEUE_PATH.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    with SCOPE_PATH.open(encoding="utf-8", newline="") as f:
        allowed = {
            row["qa_id"] for row in csv.DictReader(f)
            if row["scope_decision_draft"] == "in_scope_pending_content_review"
        }
    docs = [row for row in rows if row["qa_id"] in allowed and row["question"].strip() and row["answer"].strip()]
    if not docs:
        raise RuntimeError("No candidate documents are available in the review queue.")
    return docs


def load_retriever() -> tuple[SentenceTransformer, list[dict[str, str]], np.ndarray]:
    if not MODEL_DIR.is_dir():
        raise FileNotFoundError(f"Saved model not found at {MODEL_DIR}")
    model = SentenceTransformer(str(MODEL_DIR), device="cpu")
    docs = load_documents()
    embeddings = model.encode(
        [doc["answer"] for doc in docs],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return model, docs, embeddings


def retrieve(query: str, model: SentenceTransformer, docs: list[dict[str, str]], embeddings: np.ndarray, k: int = 3):
    query_embedding = model.encode(
        [query], convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    )[0]
    scores = embeddings @ query_embedding
    order = np.argsort(-scores)[:k]
    return [{**docs[i], "similarity": float(scores[i])} for i in order]


def query_guardrail(query: str) -> str | None:
    if EMERGENCY_RE.search(query):
        return (
            "This may describe an emergency. Please seek local emergency medical care now; "
            "do not wait for an answer from this educational prototype."
        )
    if PERSONAL_ACTION_RE.search(query):
        return (
            "I can’t advise on personal test results or starting, stopping, or changing medicine. "
            "Please contact a qualified health professional who knows your situation."
        )
    if PERSONAL_DIAGNOSIS_RE.search(query):
        return (
            "I can’t tell whether you have diabetes. Symptoms alone cannot confirm a diagnosis; "
            "please ask a qualified health professional about appropriate testing."
        )
    return None
