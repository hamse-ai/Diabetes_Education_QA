# Model and evaluation design

## Task

The system performs source-linked answer retrieval. It embeds a user's question, ranks candidate MedQuAD answers, and returns a candidate verbatim with source metadata. It does not generate answers. The cosine similarity is only a ranking value; it is not a confidence probability or factuality score.

## Compared approaches

| Approach | Representation | Role |
|---|---|---|
| TF-IDF | Word unigrams and bigrams over answer text | Lexical baseline |
| MiniLM frozen | `sentence-transformers/all-MiniLM-L6-v2` dense sentence vectors | Semantic baseline without project training |
| MiniLM fine-tuned | Same encoder with question-answer contrastive training | Project-adapted semantic retrieval |

The fine-tuning objective is MultipleNegativesRankingLoss. Each question is an anchor and its associated answer is a positive; other answers in the batch are used as negatives. The experiments use batch size 8, learning rate 2e-5, four epochs, AdamW, and seed 42.

## Experiments completed

### Run 001

Run 001 is a provisional baseline study on 175 de-duplicated, unreviewed candidate rows. It splits normalized questions 80/20 (89 train and 23 test questions). The implementation keeps all candidate answers in the retrieval index during evaluation, as expected for an answer retrieval system. See [`../reports/model_training_run_001.md`](../reports/model_training_run_001.md).

### Run 002

Run 002 applies the scope-only screen to use 156 candidate rows and holds out entire source documents. The split has 28 training documents, seven test documents, 86 training questions, 13 test questions, and 61 unambiguous training pairs after repeated test questions are purged from training. It compares the same three approaches under one split. See [`../reports/run_002_document_split.md`](../reports/run_002_document_split.md).

Run 001 and Run 002 numbers are not directly comparable because both their data and split strategy differ. Neither has medically approved data.

## Evaluation

Recall@1 and Recall@3 report whether a dataset-associated answer appears in the first one or three positions. Mean reciprocal rank (MRR) rewards higher-ranked associated answers. These metrics measure answer association, not correctness or safety. The 15-prompt evaluation draft includes source URLs, topic expectations, and boundary behavior criteria; the run predictions are in [`../reports/evaluation_draft_predictions.csv`](../reports/evaluation_draft_predictions.csv). Human relevance, support, and safety grades are blank, so do not calculate or report them as gold metrics.

See [`../reports/error_analysis_draft.md`](../reports/error_analysis_draft.md) for provisional examples and failure patterns. The draft exposes topical mismatches at moderate cosine similarity and motivates further abstention work.

## Training gate and limitations

The train script filters to rows with explicit approval fields for ordinary reviewed runs. `--include-unreviewed` must be passed for exploratory coursework runs; `--scope-draft-only` adds only a topic-level filter and must not be treated as clinical approval. Before a final model is described as validated, independently review source pages and answer pairs, freeze source-document-disjoint data splits, adjudicate an expanded test set, evaluate unsupported-query abstention, and obtain qualified safety review.

The current Streamlit interface uses phrase-based boundary rules and a provisional 0.50 similarity floor. Those are demonstration behaviors, not validated safety controls. Public deployment for health use is out of scope until data and safety review are completed.
