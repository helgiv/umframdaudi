#!/usr/bin/env python3
"""Download the exact Eurostat compressed weekly-death TSV used by the page.

Run from this directory: python fetch_data.py
The resulting data/demo_r_mwk_05.tsv.gz can be deployed alongside index.html.
Never replace the source with unverified intermediate figures.
"""
from pathlib import Path
import gzip
import sys
import requests
import hashlib
import json
from datetime import datetime, timezone

URL = 'https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_r_mwk_05?format=TSV&compressed=true'
DST = Path(__file__).resolve().parent / 'data' / 'demo_r_mwk_05.tsv.gz'

def main():
    print('Sæki gögn frá Eurostat:', URL)
    response = requests.get(URL, timeout=180, headers={'Accept': '*/*'})
    response.raise_for_status()
    content = response.content
    if content[:2] != b'\x1f\x8b':
        # In case Eurostat sends an uncompressed TSV, package it as gz ourselves.
        text = content.decode('utf-8-sig')
        if '\\TIME_PERIOD' not in text.splitlines()[0]:
            raise ValueError('Ekki gilt Eurostat-TSV. Fyrsta línan: '+text[:180])
        content = gzip.compress(content)
    sample = gzip.decompress(content)[:500].decode('utf-8-sig', errors='replace')
    if '\\TIME_PERIOD' not in sample.splitlines()[0] and '\\time' not in sample.splitlines()[0].lower():
        raise ValueError('Skráin virðist ekki vera Eurostat-TSV: '+sample[:180])
    DST.parent.mkdir(parents=True,exist_ok=True)
    DST.write_bytes(content)
    manifest = {'dataset': 'demo_r_mwk_05', 'api_url': URL, 'retrieved_at_utc': datetime.now(timezone.utc).isoformat(), 'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
    DST.with_name('provenance.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print('SHA-256:', manifest['sha256'])
    print(f'Skrifaði {DST} ({len(content):,} bæti).')
    print('Næst má setja index.html og data/ möppuna á vefþjón eða keyra: python -m http.server 8000')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('Villa:',exc,file=sys.stderr)
        sys.exit(1)
