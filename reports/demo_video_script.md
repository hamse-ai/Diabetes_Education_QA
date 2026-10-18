# Demo video script — Diabetes Education QA for Adults

**Target length:** about 8 minutes 30 seconds.  
**Recording status:** script and local Streamlit app are ready. Replace `[PUBLIC APP URL]` and `[GITHUB REPOSITORY]` after the accounts are connected and deployment is complete. Do not imply the app is publicly deployed until the URL works.

## 0:00–0:40 — Introduction

**On screen:** title slide or project README.

“This project is an English-language question-answering prototype for basic diabetes education for adults. Given a question, it retrieves an existing answer from a source-linked collection and shows where that answer came from. It does not generate medical advice or diagnose anyone. I’ll explain the data, compare three retrieval approaches, then show how the app handles an ordinary question, a retrieval mistake, and a safety-boundary question.”

## 0:40–1:35 — Problem, task, and user

**On screen:** README problem and safety-scope sections.

“The task is question-to-answer retrieval. The target user is an adult looking for general educational information in English. We chose retrieval because the available dataset contains question-answer pairs and source links, but does not provide the context spans and annotations needed for a conventional extractive question-answering model. A generated answer could sound fluent while adding unsupported details; here, the system returns a stored candidate and exposes its source.

“The boundaries matter: it should not diagnose diabetes, interpret a personal glucose result, or tell someone how to change medicine. Urgent symptoms should lead to local emergency care.”

## 1:35–2:35 — Dataset and preparation

**On screen:** `docs/medquad_audit.md`, then `data/review/medquad_scope_screen.csv` and `docs/data_review_status.md`.

“The dataset is MedQuAD, a public English medical QA collection described by Ben Abacha and Demner-Fushman. Its repository advertises 47,457 pairs. The pinned copy we inspected contained 47,441, a 16-pair discrepancy we record in the report. Searching document focus for diabetes found 447 pairs; 170 had no answer text, leaving 277 answer-bearing candidates.

“After a first-pass scope filter and exact question-answer de-duplication, the review queue had 175 rows and 112 normalized unique questions. A topic-only screen provisionally keeps 156 and flags 19 for exclusion confirmation. These are not medically approved examples. We grouped the queue into 42 source pages, because source-page checks can then be done once before reviewing their individual answers. The remaining source, currentness, and safety review is documented as pending.”

## 2:35–3:45 — Model architecture and training

**On screen:** `src/train_retriever.py`, then `src/retrieval.py`.

“The system compares three approaches. First, TF-IDF word unigrams and bigrams provide a simple lexical baseline. Second, the frozen `all-MiniLM-L6-v2` sentence encoder maps the question and candidate answers into 384-dimensional vectors. The Transformer creates contextual token representations; sentence-transformers pools them into one normalized vector, and we rank answers with cosine similarity.

“For the adapted model, the input pair is a question anchor and its matching answer as the positive. MultipleNegativesRankingLoss pushes that pair together relative to other answers in the batch. We trained for four epochs with batch size 8, learning rate 2e-5, AdamW, and seed 42 on CPU. In the document-split experiment, seven entire source pages were held out. Repeated normalized questions from those pages were purged from training.”

## 3:45–4:55 — Results and interpretation

**On screen:** `reports/run_002_document_split.md` results table.

“On the stricter, scope-screened source-document split, TF-IDF had Recall@1 of 0.154, frozen MiniLM had 0.231, and fine-tuned MiniLM had 0.462. The fine-tuned system retrieved an associated answer first for 6 of 13 test questions and in the top three for 8 of 13; its MRR was 0.587.

“This suggests fine-tuning improves ranking on these examples. The test set is small—13 queries from seven held-out pages—so one query changes Recall@1 by about 0.077. These are dataset-association metrics, not medical accuracy or safety scores. Run 001 used a different dataset and question split, so I don’t treat its scores as a direct comparison to run 002. I reran the run 002 setup cell by cell in the training notebook as run 003; it reproduced the metrics and draft rankings exactly, and the app now uses that notebook checkpoint.”

## 4:55–6:35 — App workflow and examples

**On screen:** open the deployed app at **[PUBLIC APP URL]**. If deployment is still pending, run `streamlit run app/streamlit_app.py` from the project root and demonstrate locally; say clearly that it is a local prototype.

1. Ask: **“What does diabetes mean?”** Show the retrieved definition, semantic similarity value, and recorded source link. Explain that the score is a ranking signal, not a probability.
2. Ask: **“What is low blood sugar, and what symptoms can it cause?”** The current model retrieves a general diabetes-symptom answer at similarity 0.552. Point out that the answer is related but may not answer the hypoglycemia question well. This is a real retrieval error, and the 0.50 display threshold does not catch it.
3. Ask: **“How many units of insulin should I take tonight with this glucose reading?”** Show the app declining to recommend a dose and directing the user to a qualified health professional.
4. Ask: **“What should I do if I am vomiting and have deep, rapid breathing?”** Show the emergency redirect. The app is not trying to manage the situation in chat.

“Every returned answer is labelled as an unreviewed candidate and includes its recorded source. The stored source links can be old, so the user must verify them. The current app is a classroom prototype, not a service for care.”

## 6:35–7:30 — Error analysis and limitations

**On screen:** `reports/error_analysis_draft.md` and `reports/evaluation_draft_predictions.csv`.

“The draft evaluation exposes a pattern: semantically related answers can still miss the requested topic. The A1C query retrieves a broad diabetes-management answer that happens to contain A1C information. The hypoglycemia prompt retrieves general diabetes symptoms. An emergency DKA question ranks a kidney-disease answer, although the app's phrase rule redirects this particular wording before retrieval.

“The 15 prompts have not been independently adjudicated, so I report examples rather than treating them as gold accuracy results. The phrase rules cover only anticipated wording; they do not establish comprehensive safety. The dataset itself also needs answer-level checks against current pages.”

## 7:30–8:20 — Conclusion and next work

**On screen:** report conclusion, then repository link **[GITHUB REPOSITORY]**.

“The main finding is that adapting a compact sentence encoder improved retrieval ranking over both TF-IDF and a frozen encoder on our small exploratory split. The main weakness is that retrieval can surface the wrong diabetes topic, and the data has not completed currentness or safety review. Next I would review the source pages and answers, expand and adjudicate the held-out evaluation set, then recalibrate abstention and rerun the experiments. This project demonstrates a retrieval method and its limitations; it does not demonstrate clinically reliable advice.”

## Before recording

- Replace both bracketed links only after they are live.
- Keep the app warning visible and do not enter real personal health information.
- Open the report, model script, data review status, evaluation outputs, and app before recording.
- Record one uninterrupted pass and time it; aim for 8–9 minutes.
- Be prepared to explain why Recall@1/3 and MRR fit retrieval, why similarity is not probability, how document grouping reduces leakage, and why the current results do not show medical safety.
