VENV=.venv
PY=$(VENV)/bin/python

.PHONY: run test eval smoke

run:
	$(PY) -m uvicorn app.main:app --port 8000

test:
	$(PY) -m pytest tests/ -q

eval:
	$(PY) -m app.eval

smoke:
	$(PY) scripts/smoke_gemini.py
