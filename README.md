# Diabetes Education QA for Adults

An English-language, source-grounded question-answering capstone for basic diabetes education for adults. It is presented as a general English project and is not tailored to a particular country.

## Project status

- Audience/domain: general basic diabetes education for adults, without country-specific framing.
- Interface language and initial dataset: English.
- Interface: Streamlit academic prototype; run with `streamlit run app/streamlit_app.py`.
- Data: 277 answer-bearing diabetes-focus candidates; 175 enter the exact-QA-deduplicated review queue, with 156 provisionally retained by topic-only screening. None are clinically approved for training. See [`docs/medquad_audit.md`](docs/medquad_audit.md) and [`docs/data_review_status.md`](docs/data_review_status.md).
- Experiments: lexical TF-IDF, frozen MiniLM, and fine-tuned MiniLM compared in a question split and a source-document split. See [`reports/model_training_run_001.md`](reports/model_training_run_001.md) and [`reports/run_002_document_split.md`](reports/run_002_document_split.md).
- Report: [`PDF`](reports/diabetes_education_qa_report.pdf) · [`Markdown source`](reports/report.md).
- Qualitative evaluation: [`draft predictions`](reports/evaluation_draft_predictions.csv) and [`error analysis`](reports/error_analysis_draft.md); human judgments remain pending.
- Deployment setup: [`Streamlit Community Cloud notes`](docs/deployment.md). The app is prepared but does not yet have a public URL.
- Candidate datasets and sources: [`docs/source_inventory.md`](docs/source_inventory.md).
- No patient records or identifiable health data will be collected.

The project files and app are ready for review. The answers remain unreviewed, so the prototype is not clinically validated and should not be presented as a reliable health-answering service.

## Reproduce the model experiments

Run 001 reproduces the provisional normalized-question split:

```bash
python src/train_retriever.py --include-unreviewed --split-strategy normalized_question \
  --epochs 4 --seed 42 --output reports/models/medquad_minilm_provisional
```

Run 002 uses the topic-only scope draft and holds out source documents:

```bash
python src/train_retriever.py --include-unreviewed --scope-draft-only --split-strategy doc_id \
  --epochs 4 --seed 42 --output reports/models/medquad_minilm_scope_docsplit_v002
```

Both commands explicitly train on unreviewed candidates for coursework experiments. They are not a path to clinical approval. Recreate the draft rankings for human adjudication with `python src/evaluate_draft_set.py`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The app uses the saved MiniLM checkpoint at `reports/models/medquad_minilm_scope_docsplit_v002/model/` and the scope-screened rows in `data/review/`. Keep those paths intact. The checkpoint is about 88 MB.

To rebuild the report PDF, install the `requirements.txt` dependencies and have Chrome/Chromium available, then run `python scripts/build_report_pdf.py`.

## Submission links

- GitHub repository: pending publication; this directory is a local Git repository.
- Deployed app: pending GitHub and Streamlit Community Cloud setup; see [`docs/deployment.md`](docs/deployment.md).
- Demo video: pending recording; see [`reports/demo_video_script.md`](reports/demo_video_script.md).

## Safety scope

Educational information only. The app will not diagnose, interpret personal lab results, change medicines, or replace a qualified health professional. The MedQuAD candidate answers and trained checkpoint have not completed source, currentness, or clinical safety review; the app is an academic prototype and its answers must be verified against the linked source. Urgent symptoms should prompt seeking urgent local medical care.
