"""Validate metadata, topic integrity, and the public-data privacy boundary."""
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_KEYS = {'id','doi','title','authors','year','date','venue','type','url','topics','featured','reason','discovered_on','sources','metadata_status','selection'}

def validate():
    topics = json.loads((ROOT / 'data/topics.json').read_text(encoding='utf-8'))
    papers = json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))
    ids = {t['id'] for t in topics}
    seen = set()
    for p in papers:
        assert not set(p) - PAPER_KEYS, f'Unexpected or private paper fields: {set(p) - PAPER_KEYS}'
        assert p['doi'] not in seen, 'Duplicate DOI'
        seen.add(p['doi'])
        assert p['title'] and p['authors'] and p['doi'].startswith('10.')
        assert p['url'] == 'https://doi.org/' + p['doi']
        assert p['date'] <= dt.date.today().isoformat(), 'Future publication date'
        assert p['year'] == int(p['date'][:4])
        assert p['topics'] and set(p['topics']) <= ids, 'Missing/unknown topic'
        assert not p['featured'] or p['reason'], 'Featured paper without editorial reason'
        assert p['metadata_status'] == 'verified-crossref'
        for source in p['sources']:
            assert source['name'] in ('Crossref','OpenAlex')
            assert source['url'].startswith(('https://api.crossref.org/works/','https://openalex.org/'))
    print(f'Validated {len(papers)} papers and {len(topics)} topics; no private follow-list fields')

if __name__ == '__main__':
    validate()
