# Diabetes Education Question Answering for Adults

## Abstract

This project studies source-linked question answering for basic diabetes education in English. Given a user's question, the system retrieves a candidate answer from MedQuAD rather than generating free-form medical advice. We compare a TF-IDF lexical baseline, a frozen MiniLM sentence encoder, and a contrastively fine-tuned MiniLM retriever. In a provisional query-level split, fine-tuning improves Recall@1 from 0.043 to 0.304. A second, stricter experiment uses only the scope-screened candidate subset and holds out complete source documents; fine-tuning reaches Recall@1 0.462 and MRR 0.587 on 13 held-out queries. Both datasets remain unreviewed for factual support, currentness, and clinical safety. Two separate 15-question evaluation sets have preliminary author-led relevance, answer-support, and boundary-routing judgments; independent adjudication remains pending. The Streamlit prototype is live at [diabeteseducationapp-sbpdn6uqm8uckexptjvqm3.streamlit.app](https://diabeteseducationapp-sbpdn6uqm8uckexptjvqm3.streamlit.app/), but it is not clinically validated or ready to guide care.

**Keywords:** medical question answering, information retrieval, sentence embeddings, MedQuAD, diabetes education, abstention

## 1. Problem definition and target users

The task is to help adults find basic English-language educational information about diabetes. The system ranks source-linked question-answer records for a user's question and displays the best candidate with its source. It is a retrieval problem: the model does not compose a new answer. This choice makes the information source visible and makes retrieval errors easier to inspect.

The intended user is someone seeking general educational information. The system is not intended to diagnose diabetes, interpret personal measurements, recommend a treatment, or replace a qualified health professional. Emergency and personal medication questions should be redirected rather than answered from a similar-looking FAQ. The project is general English and is not framed for a particular country.

## 2. Related work

Ben Abacha and Demner-Fushman introduced MedQuAD as a medical question-answer resource and evaluated question-entailment methods for selecting answers to consumer health questions [1]. Their paper motivates retrieving previously answered questions, but a high retrieval score does not establish that a retrieved answer is current or appropriate for an individual. The MedQuAD repository describes 47,457 question-answer pairs from 12 NIH websites and notes that answers were removed from three MedlinePlus subsets because of copyright restrictions [2].

TF-IDF provides a transparent lexical retrieval baseline: words and short phrases receive higher weights when they are distinctive in the corpus. Sentence-BERT showed how siamese Transformer encoders can map sentences to vectors that support efficient semantic search [3]. We use `sentence-transformers/all-MiniLM-L6-v2`, which produces 384-dimensional sentence embeddings intended for semantic search [4]. Contrastive fine-tuning brings a training question closer to its paired answer relative to other answers in the batch. This adapts a general sentence encoder to the project's question-to-answer matching task.

## 3. Dataset and preparation

### 3.1 Source and size

The source is MedQuAD, a public English-language collection assembled from medical information websites. We pinned the inspected upstream snapshot to commit `577bd37b96c02d1833b2c9eed2de9f96964e96cb`. That checkout contained 11,274 XML documents and 47,441 QA pairs, while the upstream README reports 47,457; we preserve this 16-pair discrepancy rather than silently treating the advertised count as the observed count. Filtering documents whose focus contains “diabet” yielded 447 pairs, of which 170 had no answer text and 277 had answers. The dataset audit and extraction procedure are in `docs/medquad_audit.md` and `src/prepare_medquad.py`.

The first-pass general-adult filter and exact question-answer de-duplication produced a 175-row review queue with 112 normalized unique questions. Its source mix is NIDDK 103, SeniorHealth 38, MedlinePlus Health Topics 11, NHLBI 7, GARD 7, GHR 5, and NINDS 4. A scope-only screen provisionally keeps 156 rows and flags 19 for exclusion confirmation: seven rare-disease collection rows, four from a population-specific US guide, and eight US financial/insurance records. These are screening decisions, not clinical approvals. Rule-based review flags prioritize 53 records; 111 have no detected flag but still need review. The 175 rows are grouped into 42 source pages to make provenance review manageable.

### 3.2 Preprocessing, quality, and limitations

The extraction preserves source URL, collection, focus, question type, question, and answer. Review preparation collapses exact duplicate question-answer pairs while retaining source provenance. Normalized question text is used to detect repeated questions when splitting. Rows are not rewritten into generated answers.

MedQuAD is broad rather than diabetes-specific. The slice contains complications, rare conditions, population-specific material, old web pages, and US service information. Its answer text reflects an older snapshot and the recorded source URL may be obsolete. The upstream license is CC BY 4.0, subject to the repository's explicit note about removed MedlinePlus answer subsets [2]. We preserve attribution and do not infer clinical approval from the license or the source's institutional status.

At the time of this report, `source_support_review`, `currentness_review`, `safety_review`, and `approved_for_training` remain incomplete. Therefore, all model results are exploratory. A source-linked draft evaluation set contains 15 questions, current official references, and expected behavior criteria. Preliminary author-led relevance, answer-support, and safety-routing judgments are recorded in `reports/evaluation_draft_predictions.csv`; independent adjudication and detailed source verification remain pending. It is excluded from training.

## 4. Methodology

### 4.1 Retrieval pipeline

For an input question, the sentence encoder produces a normalized vector. The system encodes candidate answer texts and ranks them by cosine similarity, implemented as a dot product between normalized vectors. The top answer is returned verbatim with its MedQuAD record ID, focus, source collection, and recorded URL. The cosine score is a ranking signal, not a calibrated probability or measure of medical correctness.

### 4.2 Models and training

We compare three approaches:

1. **TF-IDF word unigrams and bigrams** fitted on the answer corpus. This is the lexical baseline.
2. **Frozen MiniLM** using `sentence-transformers/all-MiniLM-L6-v2` without diabetes-specific updates.
3. **Fine-tuned MiniLM** trained with MultipleNegativesRankingLoss. Each batch contains question anchors and paired answer positives; other answers provide in-batch negatives. We use batch size 8, learning rate 2e-5, AdamW, four epochs, seed 42, and CPU training.

Run 001 uses all 175 unreviewed candidate rows and partitions normalized questions, producing 89 training and 23 test questions. Run 002 restricts the corpus to the 156-row scope-only draft, holds out seven complete source documents, and removes normalized test questions from the training partition if they recur elsewhere. It contains 28 training documents, 86 training questions, 13 test questions, and 61 unambiguous contrastive pairs. Both runs keep the answer corpus available for retrieval at test time, as it would be at inference. The second split is stricter with respect to source-page overlap.

## 5. Results

### 5.1 Run 001: normalized-question split

| Model | Recall@1 | Recall@3 | MRR | Queries |
|---|---:|---:|---:|---:|
| TF-IDF word n-grams | 0.043 | 0.217 | 0.196 | 23 |
| MiniLM frozen | 0.130 | 0.435 | 0.327 | 23 |
| MiniLM fine-tuned | 0.304 | 0.522 | 0.459 | 23 |

### 5.2 Run 002: source-document split, scope-screened candidates

| Model | Recall@1 | Recall@3 | MRR | Queries |
|---|---:|---:|---:|---:|
| TF-IDF word n-grams | 0.154 | 0.385 | 0.305 | 13 |
| MiniLM frozen | 0.231 | 0.462 | 0.392 | 13 |
| MiniLM fine-tuned | 0.462 | 0.615 | 0.587 | 13 |

In each run, fine-tuning ranks an associated answer above the baselines more often. The runs use different candidate rows and different split strategies, so their numbers should not be read as a direct before-and-after comparison. Run 002 has only 13 test queries drawn from seven test pages; one query changes Recall@1 by about 0.077. The gains are encouraging for retrieval-method development, but the sample is too small and unreviewed to support a reliability claim.

A notebook-based Run 003 repeated the same source-document split, scope-screened candidates, hyperparameters, and seed as Run 002. It reproduced the metrics and draft top-ranked predictions exactly. This is a reproducibility check, not independent evidence. The app now loads the Run 003 checkpoint; the earlier run artifacts remain available for comparison.

## 6. Evaluation and error analysis

Recall@1 measures how often an associated answer is ranked first; Recall@3 checks whether one appears in the first three; mean reciprocal rank rewards higher positions and penalizes misses. These metrics evaluate retrieval against the dataset's QA associations. They do not measure whether the answer is medically correct, current, understandable, or safe.

The 15-prompt initial review is in `reports/evaluation_draft_predictions.csv`. Its author-led, AI-assisted judgments use 1–4 relevance and support grades and a categorical routing judgment; definitions and limits are in `reports/error_analysis_draft.md`. It is not an independent or clinical review, and no result is a gold-standard label. In this set, E002 (type comparison) and E006 (hypoglycemia) are clear topic mismatches. Several apparently relevant answers still need source and currentness review. For E010–E015, the recorded app action is guardrail abstention, but routing alone does not validate safety.

To probe generalization beyond the initial prompts, we added 15 challenge queries in `data/review/evaluation_challenge_set.csv`: five paraphrases, three non-diabetes open-domain queries, three personal-care/diagnosis queries, two urgent-boundary queries, and two unsupported diabetes subdomains. The saved Run 003 model was applied with the same guardrails and 0.50 similarity threshold as the app; the ranked outputs are in `reports/evaluation_challenge_predictions.csv`. The run produced these descriptive observations:

| Challenge group | Queries | Recorded behavior | Main finding |
|---|---:|---|---|
| In-scope paraphrases | 5 | 4 shown; 1 similarity abstention | Three top results were judged directly relevant; the A1C paraphrase abstained despite being in scope. |
| Non-diabetes open-domain | 3 | 1 shown; 2 similarity abstentions | The high-blood-pressure question retrieved a diabetes/heart-disease passage and crossed the threshold (0.507), a false accept. |
| Personal care / diagnosis | 3 | 3 guardrail abstentions | The recorded routes matched the expected boundary behavior for dose and diagnosis requests. |
| Urgent boundary | 2 | 2 guardrail abstentions | The recorded emergency routes matched expectations; actual interface behavior should still be demonstrated. |
| Unsupported diabetes subdomains | 2 | 1 shown; 1 similarity abstention | A pregnancy-specific query received an unrelated diagnosis/testing candidate at 0.605, a false accept; the pump query abstained. |

All 15 challenge rows have the same preliminary author-led annotations and caveats as the initial set. The challenge prompts are hand-authored and small, so these counts are diagnostic observations, not estimates of real-world error rates. The false accepts show that a single similarity threshold cannot reliably detect domain or subdomain mismatch; threshold-only tuning also risks increasing false abstentions, as seen in the A1C paraphrase. Future evaluation should use a larger, independently judged in-scope/out-of-scope set and select any threshold on a validation set before reporting held-out results. Keep ranking relevance, source support, and safe routing as separate outcomes.

## 7. Streamlit prototype and responsible use

The Streamlit interface loads the local fine-tuned checkpoint, retrieves from the 156 scope-screened candidates, displays a source link, and surfaces other candidates for inspection. It uses simple phrase-based guardrails to direct likely emergencies to local emergency care and decline personal diagnosis or medication instructions. A similarity threshold of 0.50 is a provisional engineering setting, not one calibrated on a reviewed validation set. The interface prominently identifies the content and model as unreviewed.

The academic prototype is publicly deployed at [diabeteseducationapp-sbpdn6uqm8uckexptjvqm3.streamlit.app](https://diabeteseducationapp-sbpdn6uqm8uckexptjvqm3.streamlit.app/). The project owner reports that it is working. Public availability does not mean the content has passed source, currentness, or safety review. Do not use this prototype for clinical decisions.

## 8. Limitations and future work

The main limitation is data quality, not model capacity: the candidate answers have not been individually checked against current pages. MedQuAD's exact question-answer links also make retrieval metrics easier than realistic paraphrased patient questions. The held-out question sets are small, and rule-based guardrails cover only patterns anticipated by the authors. No clinician-reviewed answer correctness or safety score is available yet.

Next steps are to review the 42 source pages and 175 associated pairs, independently adjudicate the 15 evaluation prompts and expand them with natural paraphrases and unsupported cases, freeze source-document-disjoint train/validation/test splits, and rerun experiments only on approved material. Then calibrate abstention thresholds on held-out in-scope and out-of-scope cases, inspect errors with a qualified reviewer, and update the app and report. Future work can compare a lexical+semantic hybrid or a biomedical sentence encoder, but only under the same fixed evaluation protocol.

## 9. Conclusion

Fine-tuning MiniLM improved answer ranking over TF-IDF and the frozen encoder in both exploratory experiments. The stricter source-document split reduces a major leakage risk and still shows a promising ranking signal. However, the evaluation set reveals that semantically related diabetes answers can be wrong for the user's topic, and the source data has not completed factual, currentness, or clinical review. The valid conclusion is that compact sentence-embedding retrieval is a promising capstone method to investigate—not that this system is ready to answer health questions reliably.

## References

1. Ben Abacha, A., & Demner-Fushman, D. (2019). A question-entailment approach to question answering. *BMC Bioinformatics, 20*, 511. https://doi.org/10.1186/s12859-019-3119-4
2. Ben Abacha, A., & Demner-Fushman, D. MedQuAD repository and license notes. https://github.com/abachaa/MedQuAD
3. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. In *Proceedings of EMNLP-IJCNLP 2019* (pp. 3982–3992). https://doi.org/10.18653/v1/D19-1410
4. Sentence Transformers. `all-MiniLM-L6-v2` model card. https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
5. National Institute of Diabetes and Digestive and Kidney Diseases. Diabetes tests and diagnosis. https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis
6. Centers for Disease Control and Prevention. Diabetic ketoacidosis. https://www.cdc.gov/diabetes/about/diabetic-ketoacidosis.html
