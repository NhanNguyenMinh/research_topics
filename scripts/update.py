"""Discover by PUBLIC TOPICS only. No personal researcher list is read or required."""
import argparse
import datetime as dt
import json
import html
import os
from pathlib import Path
import re
import time
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))

def write(name, value):
    path = ROOT / 'data' / name
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)

def get(url, openalex=False):
    headers = {'User-Agent': 'ResearchTopics/1.0 (public scholarly metadata index)'}
    if openalex and os.environ.get('OPENALEX_API_KEY'):
        headers['Authorization'] = 'Bearer ' + os.environ['OPENALEX_API_KEY']
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=headers), timeout=35) as response:
                return json.load(response)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

def publication_date(item):
    dates = []
    for key in ('published-online', 'published-print', 'published'):
        parts = item.get(key, {}).get('date-parts', [[]])[0]
        if parts:
            try:
                dt.date(*(parts + [1] * (3 - len(parts))))
                dates.append('-'.join(str(n).zfill(4 if i == 0 else 2) for i, n in enumerate(parts)))
            except (ValueError, TypeError):
                pass
    return min(dates) if dates else None

def classify(title, topics):
    # Labels are a transparent title-keyword heuristic, not an assessment of quality.
    text = title.lower().replace('\u2010','-').replace('\u2011','-').replace('\u2013','-')
    return [t['id'] for t in topics if any(k in text for k in t['keywords'])]

def from_crossref(item, topics, today):
    title = html.unescape(next(iter(item.get('title', [])), '')).strip()
    date = publication_date(item)
    labels = classify(title, topics)
    doi = item.get('DOI', '').lower()
    if not title or not doi.startswith('10.') or not date or date > today or not labels:
        return None
    if item.get('type') not in ('journal-article', 'proceedings-article', 'posted-content'):
        return None
    return {
        'id': doi, 'doi': doi, 'title': title,
        'authors': [' '.join(filter(None, [a.get('given'), a.get('family')])) for a in item.get('author', [])],
        'year': int(date[:4]), 'date': date, 'venue': html.unescape(next(iter(item.get('container-title', [])), '')),
        'type': item['type'], 'url': 'https://doi.org/' + doi, 'topics': labels,
        'featured': False, 'reason': '', 'discovered_on': today,
        'metadata_status': 'verified-crossref', 'selection': 'topic-discovery',
        'sources': [{'name': 'Crossref', 'url': 'https://api.crossref.org/works/' + quote(doi, safe=''), 'checked': today}],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=24, help='Maximum new DOI lookups per run')
    args = parser.parse_args()
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date().isoformat()
    since = (now.date() - dt.timedelta(days=365)).isoformat()
    topics, queries, papers, status = read('topics.json'), read('queries.json'), read('papers.json'), read('status.json')
    by_doi = {p['doi'].lower(): p for p in papers}
    candidates, errors = {}, []
    for query in queries:
        params = {'search': query['search'], 'filter': f'from_publication_date:{since},to_publication_date:{today}', 'sort': 'publication_date:desc', 'per_page': 8, 'select': 'id,doi,title,publication_date,type'}
        try:
            result = get('https://api.openalex.org/works?' + urlencode(params), openalex=True)
            for work in result.get('results', []):
                doi = (work.get('doi') or '').removeprefix('https://doi.org/').lower()
                if doi.startswith('10.') and doi not in by_doi:
                    candidates.setdefault(doi, work['id'])
        except Exception as error:
            # Never log request URLs, credentials, or response bodies.
            errors.append(f"{query['topic']}: {type(error).__name__}")
        time.sleep(0.3)
    added, checked, rejected = 0, 0, 0
    for doi, source in list(candidates.items())[:max(0, args.limit)]:
        try:
            item = get('https://api.crossref.org/works/' + quote(doi, safe=''))['message']
            checked += 1
            paper = from_crossref(item, topics, today)
            if paper and paper['doi'] == doi:
                paper['sources'].append({'name':'OpenAlex','url':source,'checked':today})
                by_doi[doi] = paper
                added += 1
            else:
                rejected += 1
        except Exception as error:
            errors.append(f'Crossref: {type(error).__name__}')
        time.sleep(0.3)
    if added:
        write('papers.json', sorted(by_doi.values(), key=lambda p: (p['date'],p['doi']), reverse=True))
        status['data_updated_at'] = now.isoformat()
    status.update(last_attempt_at=now.isoformat(), added=added, checked=checked, rejected=rejected,
                  state='partial' if errors else 'ok', errors=errors,
                  message=f'Đã bổ sung {added} công bố; đối chiếu {checked} DOI.' + (' Một số nguồn chưa kiểm tra được; giữ lại dữ liệu hiện có.' if errors else ''))
    write('status.json', status)
    print(f'Added {added}; checked {checked}; rejected {rejected}; source errors {len(errors)}')
    if errors:
        print('; '.join(errors))
    # Surface outages as a failed workflow rather than claiming a full refresh.
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
