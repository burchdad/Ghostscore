"""Create a simple GitHub Project board (classic) and add Phase 2 issues.

Usage:
  GH_TOKEN=<token> GITHUB_REPOSITORY=owner/repo python scripts/create_project_board.py

Requires `repo` scope on the token. This uses the Projects (classic) REST API and
requires the inertia preview Accept header.
"""
import os
import sys
import glob
import re
from pathlib import Path
import requests


GITHUB_API = "https://api.github.com"


def parse_frontmatter(text):
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
                items = [i.strip().strip('"\'') for i in val[1:-1].split(',') if i.strip()]
                data[key] = items
            else:
                data[key] = val.strip().strip('"')
    data['body'] = body
    return data


def api_headers(token):
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.inertia-preview+json',
    }


def create_project(repo, token, name, body=''):
    url = f"{GITHUB_API}/repos/{repo}/projects"
    payload = {'name': name, 'body': body}
    r = requests.post(url, headers=api_headers(token), json=payload)
    if r.status_code in (200, 201):
        return r.json()
    print('Failed creating project', r.status_code, r.text)
    return None


def create_column(project_id, token, name):
    url = f"{GITHUB_API}/projects/{project_id}/columns"
    r = requests.post(url, headers=api_headers(token), json={'name': name})
    if r.status_code in (200, 201):
        return r.json()
    print('Failed creating column', r.status_code, r.text)
    return None


def find_issue_by_title(repo, token, title):
    # List issues (open + closed) and match title
    url = f"{GITHUB_API}/repos/{repo}/issues?state=all&per_page=100"
    r = requests.get(url, headers={'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'})
    if r.status_code != 200:
        print('Failed to list issues', r.status_code, r.text)
        return None
    for issue in r.json():
        if issue.get('title') == title:
            return issue
    return None


def create_card_in_column(column_id, token, issue):
    url = f"{GITHUB_API}/projects/columns/{column_id}/cards"
    payload = {'content_id': issue['id'], 'content_type': 'Issue'}
    r = requests.post(url, headers=api_headers(token), json=payload)
    if r.status_code in (200, 201):
        return r.json()
    print('Failed creating card', r.status_code, r.text)
    return None


def main():
    repo = os.environ.get('GITHUB_REPOSITORY')
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not repo or not token:
        print('Please set GITHUB_REPOSITORY and GH_TOKEN env vars')
        sys.exit(1)

    project = create_project(repo, token, 'Phase 2', 'Phase 2 workboard for Ghostscore')
    if not project:
        sys.exit(1)
    project_id = project['id']
    print('Created project:', project['name'], 'id=', project_id)

    columns = {}
    for name in ['To Do', 'In Progress', 'Done']:
        col = create_column(project_id, token, name)
        if col:
            columns[name] = col['id']
            print('Created column', name)

    # Attach phase2 issues to 'To Do'
    files = sorted(glob.glob('phase2/issues/*.md'))
    for p in files:
        text = Path(p).read_text()
        data = parse_frontmatter(text)
        if not data or 'title' not in data:
            print('Skipping', p)
            continue
        title = data['title']
        issue = find_issue_by_title(repo, token, title)
        if not issue:
            print('Issue not found (create issues first):', title)
            continue
        card = create_card_in_column(columns['To Do'], token, issue)
        if card:
            print('Added issue to project:', title)


if __name__ == '__main__':
    main()
