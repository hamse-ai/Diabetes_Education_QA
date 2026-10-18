# English diabetes QA data and source inventory

Project scope: general basic diabetes education for adults, in English, not tailored to a particular country. The training resources below are general English sources.

## Candidate datasets

| Resource | Contents and best use | Caveats |
|---|---|---|
| [MedQuAD](https://github.com/abachaa/MedQuAD) | 47,457 English medical QA pairs built from 12 NIH websites. Filter source subsets and questions/answers for diabetes (especially NIDDK and MedlinePlus Health Topics). Good primary candidate for source-linked retrieval/QA experiments. Dataset repository states CC BY 4.0; cite Ben Abacha & Demner-Fushman (2019). | Broad medical coverage, so inspect diabetes subset size and exact source URLs. Answers were removed from three MedlinePlus subsets to respect copyright; do not assume every row has answer text. Filter out diagnosis/treatment directions beyond the educational scope. |
| [Questions on Diabetes from Patients and the Public](https://doi.org/10.6084/m9.figshare.7038584) | 436 naturally asked type 2 diabetes questions: 152 from 100 clinic patients and 284 from 300 members of the public; topic tags are included. CC BY 4.0. Strong candidate for realistic queries, topic distribution, and a held-out test set. | Questions only; it does not supply answers or evidence passages. Use as query/evaluation data, not a stand-alone answer-generation training set. It includes personal-health-record-related questions that should be excluded or carefully generalized. |
| [TREC 2017 LiveQA-Med / MedQuAD judged answers](https://github.com/abachaa/MedQuAD) | Repository includes 2,479 manually judged question-answer relevance judgments for medical QA. Could provide additional evaluation protocol/examples after inspecting the files. | General medical and not diabetes-specific; check original task terms and benchmark compatibility before use. Avoid overlap with train sources/questions. |
| [HealthSearchQA](https://huggingface.co/datasets/katielink/healthsearchqa) | 3,173 consumer health questions curated to reflect common searches; useful only as possible out-of-domain/general-health questions. | Not a diabetes answer dataset. Verify its license/card and source provenance before any use. |

## Answer evidence sources

| Source | Candidate use | Notes |
|---|---|---|
| [WHO Diabetes Q&A](https://www.who.int/news-room/questions-and-answers/item/diabetes) | Definitions, types, symptoms, general management, prevention, complications | General authoritative guidance; record access date/version. |
| [WHO Diabetes fact sheet](https://www.who.int/news-room/fact-sheets/detail/diabetes) | Concise background and public-health facts | Global context, not Somalia-specific. |
| [WHO patient education manual](https://www.who.int/publications/i/item/9789290617976) | Lifestyle, eating, activity, daily self-care, complication prevention | Published by WHO Western Pacific; judge applicability and reuse terms before incorporating passages. |
## Recommended data construction

Use MedQuAD as the main source-grounded QA corpus after auditing its diabetes slice and exclusions. Use the Figshare patient/public questions to test how well retrieval handles naturally phrased consumer questions; they must not be mistaken for questions with gold answers. Build a small manually reviewed evaluation set of question, supported answer, evidence passage, and citation pairs from eligible public sources. Any machine-generated drafts must be disclosed, checked against the evidence by a human, and must not be the main training data.

Recommended normalized fields: `id`, `question`, `answer`, `context`, `source_title`, `source_url`, `source_section`, `source_dataset`, `language`, `topic`, `review_status`, `safety_tag`, `split`. Split by source document/topic and deduplicate near-identical questions to reduce leakage. Maintain a separate set for unsupported, urgent, diagnostic, medication-adjustment, and non-diabetes questions to measure safe abstention.

Do not use clinical records or personal health identifiers. Do not train the assistant to diagnose or interpret individual values such as fasting glucose, PP2BS, creatinine, or urine albumin. These measurements are outside the educational Q&A scope.

## Citation for MedQuAD

Ben Abacha, A., & Demner-Fushman, D. (2019). A question-entailment approach to question answering. *BMC Bioinformatics, 20*, 511. https://doi.org/10.1186/s12859-019-3119-4

## Citation for patient/public diabetes questions

Crangle, C. E., Bradley, C., Carlin, P. F., Esterhay, R. J., Harper, R., Kearney, P. M., Lorig, K., McCarthy, V. J. C., McTear, M., Savage, E., Tuttle, M. S., & Wallace, J. G. (2018). Questions on Diabetes from Patients and the Public [Dataset]. Figshare. https://doi.org/10.6084/m9.figshare.7038584
