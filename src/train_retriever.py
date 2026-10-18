"""Train and compare a MedQuAD question-to-answer retrieval encoder."""
import argparse
import csv
import json
import platform
import re
from collections import defaultdict
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np
import torch
from datasets import Dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GroupShuffleSplit
from sentence_transformers import SentenceTransformer, SentenceTransformerTrainer, SentenceTransformerTrainingArguments
from sentence_transformers.sentence_transformer.losses import MultipleNegativesRankingLoss

BASE_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'


def normalize(text):
    return re.sub(r'\W+', ' ', text.casefold()).strip()


def metrics(ranked_ids, relevant_ids):
    recalls = {1: [], 3: []}
    reciprocal_ranks = []
    for ranking, relevant in zip(ranked_ids, relevant_ids):
        relevant = set(relevant)
        recalls[1].append(float(bool(set(ranking[:1]) & relevant)))
        recalls[3].append(float(bool(set(ranking[:3]) & relevant)))
        rank = next((i + 1 for i, idx in enumerate(ranking) if idx in relevant), None)
        reciprocal_ranks.append(0.0 if rank is None else 1.0 / rank)
    return {
        'recall_at_1': float(np.mean(recalls[1])) if recalls[1] else 0.0,
        'recall_at_3': float(np.mean(recalls[3])) if recalls[3] else 0.0,
        'mrr': float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 0.0,
        'n_queries': len(relevant_ids),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path('data/review/medquad_review_queue.csv'))
    parser.add_argument('--output', type=Path, default=Path('models/medquad_minilm_provisional'))
    parser.add_argument('--epochs', type=int, default=4)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--split-strategy', choices=['normalized_question', 'doc_id'], default='normalized_question', help='Use normalized-question split to reproduce run 001, or source-document split to reduce page-content leakage.')
    parser.add_argument('--scope-draft-only', action='store_true', help='Restrict an exploratory run to rows marked in-scope by the scope-only draft. This is not clinical approval.')
    parser.add_argument('--include-unreviewed', action='store_true', help='Train an exploratory prototype on unreviewed source-derived candidates; never deploy these answers as clinically verified.')
    args = parser.parse_args()

    with args.input.open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    if args.scope_draft_only:
        scope_path = Path('data/review/medquad_scope_screen.csv')
        with scope_path.open(encoding='utf-8', newline='') as f:
            scope_rows = list(csv.DictReader(f))
        allowed_ids = {r['qa_id'] for r in scope_rows if r.get('scope_decision_draft') == 'in_scope_pending_content_review'}
        rows = [r for r in rows if r.get('qa_id') in allowed_ids]
    if not rows:
        raise ValueError(f'No examples in {args.input}')
    if not args.include_unreviewed and any(r.get('approved_for_training') != 'yes' for r in rows):
        rows = [r for r in rows if r.get('approved_for_training') == 'yes']
    if not args.include_unreviewed and not rows:
        raise ValueError('No approved rows. Review the queue first, or pass --include-unreviewed for an explicitly provisional experiment.')
    if not args.include_unreviewed:
        rows = [r for r in rows if r.get('scope_decision') == 'include' and r.get('source_support_review') == 'supported' and r.get('currentness_review') == 'current' and r.get('safety_review') == 'safe_general_education']
    rows = [r for r in rows if r.get('question', '').strip() and r.get('answer', '').strip()]
    if len(rows) < 20:
        raise ValueError(f'Need at least 20 reviewed examples for this exploratory run; found {len(rows)}')
    for idx, row in enumerate(rows):
        row['_index'] = idx
        row['_qnorm'] = normalize(row['question'])

    # Keep test source pages unseen. If the same normalized question occurs in both
    # page partitions, purge it from train as well to prevent exact-query leakage.
    if args.split_strategy == 'doc_id':
        groups = sorted({r.get('doc_id', '') for r in rows})
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=args.seed)
        train_idx, test_idx = next(splitter.split(np.arange(len(groups)), groups=groups))
        train_docs = {groups[i] for i in train_idx}
        test_docs = {groups[i] for i in test_idx}
        test_rows = [r for r in rows if r.get('doc_id', '') in test_docs]
        test_questions = {r['_qnorm'] for r in test_rows}
        train_rows = [r for r in rows if r.get('doc_id', '') in train_docs and r['_qnorm'] not in test_questions]
        train_questions = {r['_qnorm'] for r in train_rows}
        all_questions = {r['_qnorm'] for r in rows}
    else:
        query_rows = {}
        for row in rows:
            query_rows.setdefault(row['_qnorm'], row['question'])
        queries = list(query_rows)
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=args.seed)
        train_idx, test_idx = next(splitter.split(np.arange(len(queries)), groups=queries))
        train_questions = {queries[i] for i in train_idx}
        test_questions = {queries[i] for i in test_idx}
        train_rows = [r for r in rows if r['_qnorm'] in train_questions]
        test_rows = [r for r in rows if r['_qnorm'] in test_questions]
        train_docs = {r.get('doc_id', '') for r in train_rows}
        test_docs = {r.get('doc_id', '') for r in test_rows}
        all_questions = set(queries)

    # Multiple different answers can be relevant to one identical question in MedQuAD.
    # Exclude such ambiguous queries from contrastive training to avoid false in-batch negatives.
    answers_by_query = defaultdict(set)
    for row in train_rows:
        answers_by_query[row['_qnorm']].add(row['answer'])
    train_pairs = []
    for qnorm, answers in answers_by_query.items():
        if len(answers) == 1:
            q = next(r['question'] for r in train_rows if r['_qnorm'] == qnorm)
            train_pairs.append((q, next(iter(answers))))
    if len(train_pairs) < 8:
        raise ValueError(f'Only {len(train_pairs)} unambiguous training pairs remain; review/add data or use a different evaluation design.')

    corpus = [r['answer'] for r in rows]
    test_query_list = []
    relevant_ids = []
    for qnorm in sorted(test_questions):
        matching = [r for r in test_rows if r['_qnorm'] == qnorm]
        test_query_list.append(matching[0]['question'])
        relevant_ids.append([r['_index'] for r in matching])

    # TF-IDF reference baseline.
    tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
    doc_vectors = tfidf.fit_transform(corpus)
    q_vectors = tfidf.transform(test_query_list)
    tfidf_scores = (q_vectors @ doc_vectors.T).toarray()
    tfidf_ranked = [list(np.argsort(-scores)) for scores in tfidf_scores]
    results = {'tfidf_word_ngrams': metrics(tfidf_ranked, relevant_ids)}

    args.output.mkdir(parents=True, exist_ok=True)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    frozen = SentenceTransformer(BASE_MODEL, device=device)

    def encode_ranked(model):
        q_emb = model.encode(test_query_list, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
        a_emb = model.encode(corpus, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
        scores = q_emb @ a_emb.T
        return [list(np.argsort(-s)) for s in scores]

    results['minilm_frozen'] = metrics(encode_ranked(frozen), relevant_ids)

    dataset = Dataset.from_dict({
        'anchor': [x[0] for x in train_pairs],
        'positive': [x[1] for x in train_pairs],
    })
    train_loss = MultipleNegativesRankingLoss(frozen)
    trainer_args = SentenceTransformerTrainingArguments(
        output_dir=str(args.output / 'trainer_state'),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=8,
        learning_rate=2e-5,
        warmup_steps=0.1,
        weight_decay=0.01,
        fp16=False,
        bf16=False,
        use_cpu=(device == 'cpu'),
        save_strategy='no',
        logging_strategy='epoch',
        report_to='none',
        seed=args.seed,
        dataloader_num_workers=0,
        optim='adamw_torch',
    )
    trainer = SentenceTransformerTrainer(
        model=frozen,
        args=trainer_args,
        train_dataset=dataset,
        loss=train_loss,
    )
    train_result = trainer.train()
    model_dir = args.output / 'model'
    frozen.save(str(model_dir))
    results['minilm_finetuned'] = metrics(encode_ranked(frozen), relevant_ids)

    report = {
        'data_status': 'provisional_unreviewed' if args.include_unreviewed else 'reviewed',
        'base_model': BASE_MODEL,
        'seed': args.seed,
        'device': device,
        'input_rows': len(rows),
        'unique_queries': len(all_questions),
        'train_query_count': len(train_questions),
        'test_query_count': len(test_questions),
        'train_document_count': len(train_docs),
        'test_document_count': len(test_docs),
        'split_strategy': args.split_strategy,
        'scope_draft_only': args.scope_draft_only,
        'contrastive_training_pairs': len(train_pairs),
        'epochs': args.epochs,
        'train_loss': train_result.training_loss,
        'python_version': platform.python_version(),
        'package_versions': {},
        'results': results,
        'notes': 'Candidate answers are retrieved verbatim with source metadata. Provisional run is for method development only and is not medical validation.' if args.include_unreviewed else 'Use only after reviewing rows and source claims.',
    }
    for package in ('torch', 'sentence-transformers', 'transformers', 'scikit-learn', 'numpy', 'datasets', 'accelerate'):
        try:
            report['package_versions'][package] = version(package)
        except PackageNotFoundError:
            report['package_versions'][package] = 'not installed'
    report_path = args.output / 'results.json'
    report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    with (args.output / 'retrieval_results.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['model', 'recall_at_1', 'recall_at_3', 'mrr', 'n_queries'])
        writer.writeheader()
        for model_name, values in results.items(): writer.writerow({'model': model_name, **values})
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
