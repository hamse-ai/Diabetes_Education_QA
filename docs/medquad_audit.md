# MedQuAD initial data audit

## Snapshot inspected

Repository: https://github.com/abachaa/MedQuAD
Reference: Ben Abacha, A., & Demner-Fushman, D. (2019). A question-entailment approach to question answering. *BMC Bioinformatics, 20*, 511. https://doi.org/10.1186/s12859-019-3119-4
License stated in upstream README: CC BY 4.0. Upstream README notes answers were removed from the A.D.A.M. Medical Encyclopedia, MedlinePlus Drug Information, and MedlinePlus Herbs/Supplements collections due to MedlinePlus copyright.

The inspected GitHub snapshot contained 11,274 XML documents and 47,441 question-answer records; the README advertises 47,457 pairs, so the snapshot count is 16 lower and should be reported as an observed repository discrepancy. Filtering documents whose `<Focus>` contains “diabet” yielded 447 pairs; 170 lacked answer text, leaving 277 answer-bearing candidate rows. Most unanswered entries are from the A.D.A.M. MedlinePlus collection, consistent with the upstream copyright note.

The exported file `data/processed/medquad_diabetes_candidates.csv` retains source URL, source collection, focus, question type, question, and answer. Initial source mix:

- NIDDK: 146
- SeniorHealth: 38
- Genetic and Rare Diseases (GARD): 38
- Genetics Home Reference (GHR): 30
- MedlinePlus Health Topics: 14
- NINDS: 4
- NHLBI: 7

This is a candidate pool, not a final training/evaluation split. It contains out-of-scope material (diabetes insipidus, rare syndromes, pregnancy and pediatric topics) and needs manual scope and answer-quality review. The `scope_review` column is a first-pass heuristic only. Do not interpret it as a clinical validation. A source URL and answer text are available, but the source webpage should be checked for currentness before presenting any answer in the deployed app.

## Initial processing decision

Start with the 146 NIDDK items as the most coherent diabetes education subset. Review them for adult scope, duplicate questions, dated guidance, and safe phrasing. Keep other answer-bearing rows as potential supplemental material only after the same review. The end-user application should ground answers in approved source passages, show citations, and decline unsupported or individualized clinical questions.

## Reproduce the extraction

The project script will accept a local MedQuAD clone; the full raw repository is not stored in this project. Pin and record the upstream Git commit hash when constructing the final dataset.
