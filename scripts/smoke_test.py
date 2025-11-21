#!/usr/bin/env python3
import os
import sys
import time
import argparse
import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', required=False, help='Base URL for API, e.g. https://myapp.azurewebsites.net')
    parser.add_argument('--api-key', required=False, help='API key for x-api-key header')
    args = parser.parse_args()

    base = args.base_url or os.getenv('API_BASE_URL')
    api_key = args.api_key or os.getenv('API_KEY')

    if not base:
        print('API base URL not provided via --base-url or API_BASE_URL env var. Skipping smoke test.')
        sys.exit(0)

    headers = {}
    if api_key:
        headers['x-api-key'] = api_key

    ingest_url = base.rstrip('/') + '/api/ingest'
    print(f'Posting sample document to {ingest_url}')

    files = {'file': ('smoke.txt', b'Smoke test content', 'text/plain')}
    try:
        resp = requests.post(ingest_url, files=files, headers=headers, timeout=30)
    except Exception as e:
        print('Ingest request failed:', e)
        sys.exit(2)

    if resp.status_code not in (200, 201):
        print('Ingest failed, status:', resp.status_code, resp.text)
        sys.exit(3)

    body = resp.json()
    doc_id = body.get('doc_id')
    if not doc_id:
        print('No doc_id returned from ingest response:', body)
        sys.exit(4)

    print('Ingest accepted, doc_id=', doc_id)

    # Poll for results
    results_url = base.rstrip('/') + f'/api/results/{doc_id}'
    timeout = 60
    interval = 5
    elapsed = 0
    while elapsed < timeout:
        try:
            r = requests.get(results_url, headers=headers, timeout=10)
        except Exception as e:
            print('Get results request failed:', e)
            r = None
        if r and r.status_code == 200:
            print('Result available:', r.json())
            print('Smoke test passed')
            sys.exit(0)
        time.sleep(interval)
        elapsed += interval
        print('Waiting for result...', elapsed)

    print('Result not available within timeout')
    sys.exit(5)


if __name__ == '__main__':
    main()
