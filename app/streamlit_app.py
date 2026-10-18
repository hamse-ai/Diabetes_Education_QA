"""Streamlit interface for the source-linked diabetes QA prototype."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.retrieval import SIMILARITY_THRESHOLD, load_retriever, query_guardrail, retrieve

st.set_page_config(page_title="Diabetes Education QA", page_icon="🩺", layout="centered")
st.title("Diabetes Education QA")
st.caption("A source-linked retrieval prototype for basic diabetes education in English")

st.warning(
    "Academic prototype. Candidate answers come from an unreviewed MedQuAD subset and may be outdated. "
    "Use the linked source to verify information; this tool is not for diagnosis or treatment decisions."
)

with st.expander("What this tool can and cannot do"):
    st.write(
        "The system retrieves a candidate answer from a small diabetes question-answer collection and "
        "shows its source. It does not generate or verify medical advice, diagnose conditions, interpret "
        "personal results, or recommend medication changes. Source links may point to older pages."
    )

@st.cache_resource(show_spinner="Loading the local retrieval model…")
def get_resources():
    return load_retriever()

try:
    model, documents, answer_embeddings = get_resources()
except Exception as exc:
    st.error("The local model or candidate data could not be loaded. Check the project setup instructions.")
    st.code(str(exc))
    st.stop()

query = st.text_input(
    "Ask a general diabetes education question",
    placeholder="For example: What is an A1C test?",
    max_chars=500,
)

if st.button("Find a source", type="primary", disabled=not query.strip()):
    blocked = query_guardrail(query)
    if blocked:
        st.error(blocked)
    else:
        with st.spinner("Searching the in-scope candidate records…"):
            results = retrieve(query.strip(), model, documents, answer_embeddings, k=3)
        best = results[0]
        # Cosine similarity is a ranking signal, not a calibrated probability.
        if best["similarity"] < SIMILARITY_THRESHOLD:
            st.info(
                "I couldn’t find a sufficiently similar candidate answer in this small collection. "
                "Please consult a trusted health source or a qualified health professional."
            )
        else:
            st.subheader("Closest candidate answer")
            st.caption(
                f"Semantic similarity: {best['similarity']:.3f} (not a probability or a correctness score)"
            )
            st.text(best["answer"])
            st.markdown(f"**Topic:** {best['focus']}  \n**Question in source:** {best['question']}")
            if best.get("source_url"):
                st.markdown(f"[Open the recorded source page]({best['source_url']})")
            st.caption(
                f"Source collection: {best['source_collection']} · Record: {best['qa_id']}. "
                "This answer has not been independently checked for currentness or safety."
            )
            with st.expander("Other retrieved candidates"):
                for item in results[1:]:
                    st.markdown(f"**{item['focus']}** · similarity {item['similarity']:.3f}")
                    st.write(item["question"])

st.divider()
st.caption(
    "For urgent symptoms, seek local emergency care. For individual concerns, contact a qualified "
    "health professional. Similarity scores do not measure medical correctness."
)
