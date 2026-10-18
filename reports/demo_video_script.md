# Demo video script — Diabetes Education QA for Adults

**Target length:** about 9 minutes.
**Recording status:** not recorded. Do not claim public deployment until the deployed URL works. The app can be demonstrated locally.

## 0:00–0:35 — Introduction

**On screen:** title slide or README.

“This is an English-language question-answering prototype for basic diabetes education for adults. It retrieves a stored answer from a source-linked collection rather than generating new text. I’ll explain the data and model, show how fine-tuning works, compare the experiments, and demonstrate both successful and failed retrievals and the app’s safety boundaries.”

## 0:35–1:20 — Problem, task, and user

**On screen:** README problem and safety-scope sections.

“The task is question-to-answer retrieval for adults looking for general diabetes education. We chose retrieval because MedQuAD provides question-answer records and source links, but not the context-span annotations needed to train an extractive question-answering model. Retrieval lets us return the stored passage and expose its provenance instead of composing an answer that may add unsupported information.

“The intended system does not diagnose, interpret personal results, or recommend treatment changes. Urgent symptoms should be directed to local emergency care.”

## 1:20–2:15 — Dataset and preparation

**On screen:** `docs/medquad_audit.md`, `data/review/medquad_scope_screen.csv`, and `docs/data_review_status.md`.

“MedQuAD is a public English medical question-answer collection. Its repository reports 47,457 pairs. The pinned snapshot we inspected contained 47,441, so we record that 16-pair discrepancy. The diabetes-focus filter found 447 records: 170 had no answer text and 277 had answers.

“After exact question-answer de-duplication, the review queue had 175 rows and 112 normalized unique questions. A topic-only screen provisionally kept 156 and flagged 19 for confirmation. These rows have not passed answer-level source, currentness, or safety review. We grouped them by source page to make provenance review easier.”

## 2:15–4:15 — Model architecture, data flow, and training

**On screen:** `notebooks/02_train_retriever.ipynb` (cells for the split, pairs, baselines, and training); then `src/retrieval.py` and the saved model’s `modules.json`.

“The serving model is `sentence-transformers/all-MiniLM-L6-v2`. It uses a shared six-layer Transformer sentence encoder for both the user question and each stored answer. The tokenizer converts text into token IDs. The Transformer produces contextual token representations; mean pooling combines those into a 384-dimensional sentence vector, and the model normalizes the vector.

“At inference, the app encodes the question, compares it with precomputed answer vectors using a dot product, and returns the highest-ranked stored answer with its topic and source link. Because the vectors are normalized, the dot product is cosine similarity. The score is a ranking signal, not a probability or correctness estimate. The model retrieves whole stored answers; it does not generate text or compare the question and answer through a cross-encoder.

“We compared three approaches. TF-IDF over word unigrams and bigrams is the lexical baseline. Frozen MiniLM tests the pretrained encoder without task-specific updates. Fine-tuned MiniLM tests whether adapting that same encoder to question-to-answer pairs improves ranking.

“For training, each example is a question anchor paired with its known answer as the positive. `MultipleNegativesRankingLoss` encourages the paired question and answer to be close while treating the other answers in the batch as negatives. With batch size 8, each anchor has up to seven in-batch negatives. That is efficient, but a semantically valid alternative answer could be treated as a negative, one reason to interpret the results cautiously. We trained the encoder for four epochs with learning rate 2e-5, AdamW, weight decay 0.01, and seed 42 on CPU. There is no task-specific classification head.

“The source-document split kept seven documents and 13 questions for test and removed repeated normalized test questions from the training partition. Training used 61 unambiguous pairs. At retrieval time the full candidate index is available, as it would be in the app; held-out documents were excluded from training, not removed from the searchable answer collection.”

## 4:15–5:20 — Results and interpretation

**On screen:** `reports/run_002_document_split.md` or the `results.json` for notebook Run 003.

“On the source-document split, TF-IDF had Recall@1 of 0.154, frozen MiniLM 0.231, and fine-tuned MiniLM 0.462. Fine-tuning retrieved an associated answer first for 6 of 13 queries and in the top three for 8 of 13; MRR was 0.587.

“This indicates better ranking on this small split, not better medical correctness. One query changes Recall@1 by about 0.077. Run 001 used a different split and candidate set, so I don’t compare its scores as if it were the same test. Notebook Run 003 repeats Run 002’s setup and reproduces its metrics; that checks reproducibility, not independent generalization.”

## 5:20–6:50 — App workflow and examples

**On screen:** open the deployed app at [diabeteseducationapp-sbpdn6uqm8uckexptjvqm3.streamlit.app](https://diabeteseducationapp-sbpdn6uqm8uckexptjvqm3.streamlit.app/).

1. Ask: **“What does diabetes mean?”** Show the answer, source link, and similarity. Explain that the user should verify the old recorded source.
2. Ask: **“What is low blood sugar, and what symptoms can it cause?”** The model retrieves a general diabetes-symptom answer at about 0.552. Explain why the topic overlap does not answer the question.
3. Ask: **“How is high blood pressure treated?”** The challenge run shows an unrelated diabetes/heart-disease passage at about 0.507, just above the 0.50 display threshold. Explain this false accept and that the threshold is provisional.
4. Ask: **“How many units of insulin should I take tonight with this glucose reading?”** Show the personal-dose guardrail response.
5. Ask: **“What should I do if I am vomiting and have deep, rapid breathing?”** Show the emergency response directing the user to local emergency care.

“The app displays stored candidate text, provenance, and a warning that the answer has not been independently checked. The similarity score is not medical confidence. This is an academic prototype, not a care service.”

## 6:50–7:55 — Evaluation and error analysis

**On screen:** `reports/error_analysis_draft.md`, `reports/evaluation_draft_predictions.csv`, and `reports/evaluation_challenge_predictions.csv`.

“The original 15 prompts include two clear retrieval misses: a type 1 versus type 2 question retrieves a type 2 risk answer, and a hypoglycemia question retrieves general diabetes symptoms. The 15-query challenge set adds paraphrases, unrelated topics, personal-care questions, urgent cases, and unsupported subdomains. It revealed two false accepts: high blood pressure and pregnancy-specific questions receive unrelated diabetes candidates. The A1C paraphrase is a false abstention.

“These are hand-authored, AI-assisted author-review judgments, not independent or clinical labels. The samples are too small to estimate real-world error or safety rates. They do show why retrieval relevance, source support, and boundary routing need separate evaluation.”

## 7:55–8:35 — Limitations and next work

**On screen:** report limitations and review-status documentation.

“The most important limitation is the data: source support, currentness, and clinical safety review are incomplete. The evaluation samples are small and hand-authored, and similarity thresholding misses both unsupported-domain questions and some valid paraphrases. Next steps are independent review of answers and evaluation labels, a larger paraphrased and out-of-scope test set, validation-based threshold selection, and rerunning experiments on approved data.”

## 8:35–9:00 — Conclusion

**On screen:** report conclusion and repository link **[GITHUB REPOSITORY]**.

“Fine-tuning improved retrieval ranking over TF-IDF and frozen MiniLM on our exploratory source-document split. But relevant-sounding retrieval can still be wrong, and the content is not clinically validated. This project demonstrates a compact retrieval method and a careful analysis of its limits; it does not demonstrate reliable medical advice.”

## Before recording

- Confirm the public app link loads before recording; the project owner currently reports it is working.
- Keep the prototype warning visible and use only the prepared example prompts.
- Open the notebook, `src/retrieval.py`, model results, evaluation files, and app before recording.
- Be prepared to explain the shared encoder, pooling and normalization, cosine ranking, in-batch negatives, split design, and why retrieval metrics do not measure medical correctness.
- Avoid saying that data review, independent evaluation, clinical validation, or public deployment is complete.
