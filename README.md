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

## Notebook workflows

Open the notebooks in order from JupyterLab (`jupyter lab`):

1. [`01_dataset_audit.ipynb`](notebooks/01_dataset_audit.ipynb) explores the candidate and review datasets.
2. [`02_train_retriever.ipynb`](notebooks/02_train_retriever.ipynb) compares TF-IDF, frozen MiniLM, and a fine-tuned retriever cell by cell. The completed `v003` run is saved under `reports/models/`; the existing `v001` and `v002` checkpoints are retained.
3. [`03_evaluation_review.ipynb`](notebooks/03_evaluation_review.ipynb) regenerates a separate v003 prediction file, then displays retrieval scores and the human-review queue.

The current dataset has not passed source, currentness, or clinical safety review. The training notebook labels runs provisional and uses a separate output directory. Change its `RUN_NAME` for each additional run; it refuses to overwrite an existing directory.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The app now uses the notebook-trained checkpoint at `reports/models/medquad_minilm_scope_docsplit_notebook_v003/model/` and the scope-screened rows in `data/review/`.

To rebuild the report PDF, install the `requirements.txt` dependencies and have Chrome/Chromium available, then run `python scripts/build_report_pdf.py`.

## Submission links

- GitHub repository: pending publication; this directory is a local Git repository.
- Deployed app: pending GitHub and Streamlit Community Cloud setup; see [`docs/deployment.md`](docs/deployment.md).
- Demo video: pending recording; see [`reports/demo_video_script.md`](reports/demo_video_script.md).

## Safety scope

Educational information only. The app will not diagnose, interpret personal lab results, change medicines, or replace a qualified health professional. The MedQuAD candidate answers and trained checkpoint have not completed source, currentness, or clinical safety review; the app is an academic prototype and its answers must be verified against the linked source. Urgent symptoms should prompt seeking urgent local medical care.
