"""Fail if private registry identifiers or files enter Git or the Pages artifact."""
import subprocess
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
tracked=subprocess.check_output(['git','-c','safe.directory='+str(ROOT),'ls-files'],cwd=ROOT,text=True).splitlines()
for name in tracked:
    assert name not in {'data/researchers.json','data/author-candidates.json','data/seeds.json','data/unresolved-seeds.json'}, 'Private file tracked'
    assert not any(part in name.lower() for part in ('watchlist','researchers.json','author-candidates','_local.py','bootstrap.py','resolve_authors.py')), 'Private input/helper tracked'
    text=(ROOT/name).read_text(encoding='utf-8')
    assert not re.search(r'https://scholar\.google\.[^\s"\']+[?&]user=[A-Za-z0-9_-]{12}',text), f'Private profile URL found: {name}'
    if name.endswith('.json'):
        assert not re.search(r'"(?:openalex_id|identity_evidence|researchers)"\s*:',text), f'Private follow-list field found: {name}'
    assert not re.search(r'gh[pousr]_[A-Za-z0-9]{25,}',text), 'Credential-like value found'
print(f'Checked {len(tracked)} tracked public files; no registry or follow-list identifiers')
