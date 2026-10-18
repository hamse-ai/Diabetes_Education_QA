"""Extract answer-bearing MedQuAD records whose document focus mentions diabetes."""
import argparse
import csv
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


def classify_scope(focus: str) -> str:
    focus_lower = focus.lower()
    if 'insipidus' in focus_lower:
        return 'exclude_diabetes_insipidus'
    if any(term in focus_lower for term in ('gestational', 'pregnancy', 'neonatal', 'maturity-onset', 'infant', 'child', 'teen')):
        return 'review_special_population'
    if any(term in focus_lower for term in ('rare', 'syndrome', 'maternally inherited', 'monogenic', 'mastopathy', 'brittle')):
        return 'review_rare_or_special_condition'
    return 'candidate_general_adult_education'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='Path to cloned MedQuAD repository')
    parser.add_argument('--output', type=Path, default=Path('data/processed/medquad_diabetes_candidates.csv'))
    args = parser.parse_args()
    records = []
    all_docs = all_pairs = focus_pairs = focus_empty = 0
    by_source = Counter()
    for path in args.input.rglob('*.xml'):
        try:
            doc = ET.parse(path).getroot()
        except ET.ParseError:
            continue
        all_docs += 1
        source = doc.attrib.get('source', '')
        url = doc.attrib.get('url', '')
        doc_id = doc.attrib.get('id', '')
        focus = ' '.join((doc.findtext('Focus') or '').split())
        for pair in doc.findall('.//QAPair'):
            all_pairs += 1
            question_node = pair.find('Question')
            question = ' '.join((question_node.text or '').split()) if question_node is not None else ''
            answer = ' '.join((pair.findtext('Answer') or '').split())
            if not re.search(r'\bdiabet', focus, re.I):
                continue
            focus_pairs += 1
            if not answer:
                focus_empty += 1
                continue
            collection = path.parent.name
            by_source[collection] += 1
            records.append({
                'doc_id': doc_id,
                'qa_id': question_node.attrib.get('qid', '') if question_node is not None else '',
                'source': source,
                'source_collection': collection,
                'source_url': url,
                'focus': focus,
                'question_type': question_node.attrib.get('qtype', '') if question_node is not None else '',
                'question': question,
                'answer': answer,
                'scope_review': classify_scope(focus),
                'review_status': 'unreviewed',
            })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(records[0]) if records else []
    with args.output.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    print(f'XML documents: {all_docs}')
    print(f'QA pairs observed: {all_pairs}')
    print(f'Diabetes-focus pairs: {focus_pairs}; missing answers: {focus_empty}; exported: {len(records)}')
    print('Answered rows by collection:')
    for collection, count in sorted(by_source.items()):
        print(f'  {collection}: {count}')
    print(f'Wrote {args.output}')


if __name__ == '__main__':
    main()
