"""Create Phase 2 GitHub issues from markdown files.

Usage:
  GH_TOKEN=<token> GITHUB_REPOSITORY=owner/repo python scripts/create_phase2_issues.py

This script will iterate `phase2/issues/*.md` and create issues.
"""
import os
import glob
import re
import sys
import json
from pathlib import Path

import requests


def parse_frontmatter(text):
    # simple YAML-style frontmatter parser for title, labels, milestone
    m = re.match(r"---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None
    meta, body = m.group(1), m.group(2).strip()
    data = {}
    for line in meta.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            key = k.strip()
            val = v.strip()
            if val.startswith('[') and val.endswith(']'):
                # list
                items = [i.strip().strip('"\'') for i in val[1:-1].split(',') if i.strip()]
                data[key] = items
            else:
                data[key] = val.strip().strip('"')
    data['body'] = body
    return data


def create_issue(repo, token, title, body, labels=None):
    url = f'https://api.github.com/repos/{repo}/issues'
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    payload = {'title': title, 'body': body}
    if labels:
        payload['labels'] = labels
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code in (200, 201):
        print('Created', title)
        return r.json()
    else:
        print('Failed to create', title, r.status_code, r.text)
        return None


def main():
    repo = os.environ.get('GITHUB_REPOSITORY')
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not repo or not token:
        print('Please set GITHUB_REPOSITORY and GH_TOKEN env vars')
        sys.exit(1)

    files = sorted(glob.glob('phase2/issues/*.md'))
    if not files:
        print('No issue files found in phase2/issues')
        sys.exit(0)

    for p in files:
        text = Path(p).read_text()
        data = parse_frontmatter(text)
        if not data or 'title' not in data:
            print('Skipping', p, '— missing frontmatter')
            continue
        title = data['title']
        body = data.get('body', '') + '\n\n' + '\n'.join([f'*Milestone*: {data.get("milestone") or "Phase 2"}'])
        labels = data.get('labels')
        create_issue(repo, token, title, body, labels)


if __name__ == '__main__':
    main()
