# Exploratory retrieval run 002: source-document holdout

## Purpose

Check whether the retrieval comparison remains useful when whole source pages are held out, and exclude the 19 scope-screened rows from this exploratory corpus. The remaining 156 examples are still **unreviewed**; “in scope” here means only a topic-level screening draft.

## Configuration

- Input: `data/review/medquad_review_queue.csv`, filtered by `data/review/medquad_scope_screen.csv` to 156 candidate rows.
- Split: `doc_id`, 80/20 with seed 42. Seven documents and 13 normalized questions form the test set; repeated normalized test questions are purged from training even if they appear in other documents.
- Training partition: 28 source documents, 86 unique questions, 61 unambiguous question-answer pairs.
- Candidate answer index at evaluation: all 156 candidate answers, as at retrieval time.
- TF-IDF: word unigrams and bigrams on candidate answer text.
- Dense models: `sentence-transformers/all-MiniLM-L6-v2`, frozen baseline and fine-tuned model.
- Fine-tuning: MultipleNegativesRankingLoss, batch size 8, learning rate 2e-5, four epochs, AdamW, seed 42, CPU.
- Device/software: CPU; see `results.json` for Python and package versions.

## Results

| Model | Recall@1 | Recall@3 | MRR | Test queries |
|---|---:|---:|---:|---:|
| TF-IDF word n-grams | 0.154 | 0.385 | 0.305 | 13 |
| MiniLM frozen | 0.231 | 0.462 | 0.392 | 13 |
| MiniLM fine-tuned | 0.462 | 0.615 | 0.587 | 13 |

The fine-tuned model retrieves an associated answer at rank 1 for 6 of 13 test questions and in the top 3 for 8 of 13. The final training loss is 0.4242. Run artifacts are `reports/models/medquad_minilm_scope_docsplit_v002/`.

## Interpretation

Fine-tuning ranks associated source answers above the frozen and lexical baselines on this small source-held-out split. The split is stricter than run 001 with respect to source pages, but seven test documents and 13 queries still produce wide uncertainty. Results remain association-based retrieval scores, not medical factuality or safety scores. The rows have not passed answer-level source, currentness, or safety review, so this model remains exploratory.

## Reproduction

```bash
python src/train_retriever.py \
  --input data/review/medquad_review_queue.csv \
  --scope-draft-only \
  --include-unreviewed \
  --split-strategy doc_id \
  --epochs 4 \
  --seed 42 \
  --output reports/models/medquad_minilm_scope_docsplit_v002
```
