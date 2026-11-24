#!/bin/bash
# Run RoleFit Agent locally: no database, no key needed (demo mode),
# or the real Gemini path when GEMINI_API_KEY is set in the environment.
set -e
cd "$(dirname "$0")/.."
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
if ! .venv/bin/python -c "import fastapi" 2>/dev/null; then
  TMPDIR=~/workspace/.pip-tmp .venv/bin/pip install --no-cache-dir -q -r requirements.txt
fi
exec .venv/bin/python -m uvicorn app.main:app --port 8000
