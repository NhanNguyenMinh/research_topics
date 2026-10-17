"""Build an allowlisted static artifact, excluding private inputs and scripts."""
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
def main():
    target = ROOT / 'dist'
    target.mkdir(exist_ok=True)
    # Never copy the workspace, repository root, or local researcher files.
    files = [(ROOT / 'web' / name, target / name) for name in ('index.html','styles.css','app.js','model.mjs')]
    files += [(ROOT / 'data' / name, target / 'data' / name) for name in ('papers.json','topics.json','status.json')]
    allowed = {dest.resolve() for _, dest in files} | {(target / '.nojekyll').resolve()}
    unexpected = [p for p in target.rglob('*') if p.is_file() and p.resolve() not in allowed]
    if unexpected:
        raise RuntimeError('Unexpected files in static output; inspect before publishing: ' + ', '.join(str(p) for p in unexpected))
    for source, dest in files:
        dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(source, dest)
    (target / '.nojekyll').write_text('',encoding='utf-8')
    print(f'Built {len(files)} files in {target}')
if __name__ == '__main__':
    main()
