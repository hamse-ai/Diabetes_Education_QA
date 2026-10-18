# Draft evaluation and error analysis

## Status

`evaluation_draft_predictions.csv` contains model rankings for the 15 prompts in `data/review/evaluation_set_draft.csv`. The expected source/topic labels and all human judgment columns remain pending. This is an author-led qualitative inspection, not a gold-standard evaluation or clinical review.

## Observed retrieval behavior

| Example | Prompt topic | Top retrieved topic | Provisional observation |
|---|---|---|---|
| E001 | Diabetes definition | Diabetes | The returned passage begins with a general diabetes definition. |
| E003 | Common symptoms | Type 1 and type 2 guide | The answer lists common diabetes symptoms, although its source content is dated and requires checking. |
| E004 | Diagnostic tests | Diagnosis of diabetes and prediabetes | The retrieved passage discusses diagnostic tests; current thresholds and wording still require source review. |
| E007 | Kidney complications | Diabetic kidney disease | The candidate is topically aligned but includes old epidemiological details that should not be repeated without checking. |
| E008 | Eye complication prevention | Diabetic retinopathy | The retrieved answer discusses retinopathy and eye exams; its dated frequency claim needs current verification. |
| E002 | Type 1 versus type 2 | Type 2 risk factors | Related to diabetes types, but the candidate may not answer the requested comparison. |
| E005 | A1C definition | Diabetes management | The answer contains a definition of A1C, but this is incidental material in a broader answer, making grounding harder to inspect. |
| E006 | Hypoglycemia | General diabetes symptoms | The system misses the requested topic despite a similarity score of 0.552. This is a concrete counterexample to treating similarity as confidence. |

The 0.50 similarity floor allows E005 and E006 to display candidate answers. Therefore it is only a demonstration setting and does not safely determine answerability. The interface explicitly labels the result as a candidate and requires checking its source, but the current data should not be used for care.

## Boundary prompts

The draft includes six cases intended to exercise the app's phrase-based boundary routes: DKA/emergency information (E010), personal diagnosis (E011), personal insulin dosing (E012), medication stopping (E013), urgent symptoms (E014), and individualized medicine selection during pregnancy/kidney disease (E015). The current rule set routes these prompts away from ordinary retrieval. This count is a code-path observation on a small hand-authored set; it is not evidence of safety or coverage on real user traffic.

## Next evaluation work

Independent reviewers should score each top result for relevance, answer support, and safety (suggested 1–4 relevance scale and categorical safety judgment), then adjudicate disagreements. Expand the set with varied paraphrases, questions outside the corpus, personal measurements, medication requests, and urgent presentations. Report retrieval Recall@1/3 and MRR only after gold relevance judgments are frozen; report abstention coverage and unsafe-answer rate separately.
