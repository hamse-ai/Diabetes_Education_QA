# Provisional model training run 001

Date: 2026-10-18

## Objective

Compare a lexical baseline, a frozen semantic encoder, and a fine-tuned semantic encoder for retrieving a MedQuAD answer record given a question. This is an answer-retrieval experiment; it does not generate new medical advice or establish that any answer is medically correct.

## Data and split

- Upstream dataset: MedQuAD, repository commit `577bd37b96c02d1833b2c9eed2de9f96964e96cb`.
- Input: `data/review/medquad_review_queue.csv`.
- 175 de-duplicated exact question-answer pairs after the first-pass general adult scope heuristic.
- 112 normalized unique questions.
- Split by normalized question, seed 42: 89 train questions, 23 held-out test questions.
- The contrastive objective used 69 training pairs. Queries paired with multiple distinct answers were left out of contrastive training to reduce false-negative labels.
- The answer corpus for retrieval contained the 175 candidate answers, with source metadata.
- **Data status: provisional and unreviewed.** Source, factual support, currentness, safety, and scope review columns are not complete. Some geographically specific or specialized records may remain in the candidate pool.

## Models and configuration

- TF-IDF word unigrams/bigrams, fitted on answer text.
- Frozen `sentence-transformers/all-MiniLM-L6-v2`.
- Fine-tuned `sentence-transformers/all-MiniLM-L6-v2` using `MultipleNegativesRankingLoss`, batch size 8, learning rate 2e-5, 4 epochs, seed 42.
- CPU-only PyTorch; no GPU was used.

## Results

| Model | Recall@1 | Recall@3 | MRR | Held-out queries |
|---|---:|---:|---:|---:|
| TF-IDF word n-grams | 0.043 | 0.217 | 0.196 | 23 |
| MiniLM frozen | 0.130 | 0.435 | 0.327 | 23 |
| MiniLM fine-tuned | 0.304 | 0.522 | 0.459 | 23 |

Training loss was 0.3551 at the end of epoch 4. Lower training loss alone is not evidence of better answer correctness.

## Interpretation and limits

In this provisional split, fine-tuning ranked an accepted answer higher than the frozen model and TF-IDF on more held-out questions. The test set is only 23 questions, so these scores are highly uncertain and may change materially with a different split. The candidate records have not been clinically reviewed; retrieval scores do not measure factual accuracy, readability, safety, or appropriateness for a particular person. This model must not power a public health advice app until data review, citation checks, out-of-scope/abstention evaluation, and human error analysis are complete.

## Artifacts

- Training script: `src/train_retriever.py`
- Trained model: `reports/models/medquad_minilm_provisional/model/`
- Machine-readable scores and setup metadata: `reports/models/medquad_minilm_provisional/results.json`
- Score table: `reports/models/medquad_minilm_provisional/retrieval_results.csv`

## Environment

Python 3.13.5; torch 2.14.1+cpu; sentence-transformers 5.7.0; transformers 5.20.1; scikit-learn 1.9.1; pandas 3.0.6; datasets 4.8.5; accelerate 1.15.0. The working virtual environment is temporary at `/tmp/diabetes-qa-venv`; recreate it from the project requirements and install the CPU PyTorch build for a persistent rerun.
