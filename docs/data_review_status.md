# Data review: current status and next decisions

## Scope

The project is general English basic diabetes education for adults. This screening pass organizes the 175 deduplicated candidate Q/A rows in `data/review/medquad_review_queue.csv` for human review. It does not verify answer accuracy or clinical safety.

## Automated triage results

The rules in `src/triage_medquad.py`, which creates `data/review/medquad_triage.csv`, only detect likely review triggers in the focus, question, or answer. Mentions can be incidental, so flags do not automatically mean a row must be excluded.

| Triage bucket | Rows | Meaning |
|---|---:|---|
| Likely out-of-scope review | 11 | Rare/syndromic focus or a US-specific population focus; confirm before excluding. |
| Priority human review | 53 | Contains at least one special-topic trigger such as pregnancy/youth, individualized dosing, old research, or US service details. |
| General candidate needing source review | 111 | No trigger found; still needs source, currentness, scope, and safety review. |

Detected triggers (overlapping): individualized_dosing_language: 1, location_or_context_specific_detail: 15, mentions_pregnancy: 27, mentions_youth: 25, population_specific_us_context: 10, rare_or_syndromic_focus: 7, research_may_be_outdated: 6. These are regex counts, not independent excluded records.

## Scope-only draft

`data/review/medquad_scope_screen.csv` applies transparent topic-level rules: 156 rows are provisionally in scope pending content review, and 19 are flagged for exclusion confirmation (7 from GARD, 4 from the American Indian-specific guide, and 8 from US financial/insurance guidance). This is an administrative scope pass only; it does not validate any answer. Reproduce it with `python src/screen_medquad_scope.py`.

## Source-page review sheet

`data/review/source_document_review.csv` groups all 175 candidate pairs under 42 source pages and leaves reviewer fields blank. Check each page's current authoritative location, then use the associated QA IDs to check each answer. Recreate the sheet with `python src/build_source_review_sheet.py`. Page-level checks are not a substitute for pair-level support and safety judgments.

## Dataset observations

- The queue has 175 rows from 7 source collections; 103 rows (59%) are from NIDDK.
- The first-pass pool is dominated by NIDDK and SeniorHealth items, and the exact-Q/A de-duplication still leaves many near-duplicate questions.
- The queue includes broad adult education as well as complications, research questions, finance/access material, and narrow or population-specific items.
- The answers are inherited from a 2019 MedQuAD release assembled from source pages; a row's stored URL is not evidence that its answer is still current. Check the live authoritative page and record the review date.
- The upstream snapshot count discrepancy and license notes are recorded in `medquad_audit.md`.

## Review protocol

Review every row against its live source. For each, record: (1) adult/general scope, (2) answer accurately supported by that source, (3) currentness, (4) safe educational wording, (5) whether approved for training, and a short rationale. If the source is unavailable, the answer is stale, or the question requests individualized diagnosis/dosing/treatment, do not approve it as written. Keep an excluded-row log and preserve source attribution.

A second reviewer should independently check all proposed training approvals and all safety-sensitive rows. This project team is not a clinical review panel; final clinical safety claims require qualified subject-matter review.

## Evaluation set status

`data/review/evaluation_set_draft.csv` is a small, source-linked draft for retrieval and abstention evaluation. It contains prompts, expected topic/source, and behavior criteria rather than model-written medical answers. Its human relevance and safety judgments are **pending**. Do not report it as a validated gold set until independent reviewers check the expected source/topic mapping and adjudicate disagreements. Keep it outside model training and model selection until frozen.
