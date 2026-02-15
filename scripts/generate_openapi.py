"""Export the FastAPI OpenAPI schema to a file for CI or docs.

Run: python scripts/generate_openapi.py
"""
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.main import app

out = app.openapi()

os.makedirs('docs', exist_ok=True)
with open('docs/openapi.json', 'w') as f:
    json.dump(out, f, indent=2)

print('Wrote docs/openapi.json')
