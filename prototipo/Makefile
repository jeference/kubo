# Run from prototipo/. Recipes work under both cmd.exe and sh (GNU make on Windows
# uses whichever it finds): forward slashes inside quotes are accepted by both.
ifeq ($(OS),Windows_NT)
PYTHON := ".venv/Scripts/python.exe"
else
PYTHON := .venv/bin/python
endif

.PHONY: backend frontend

backend:
	cd backend && $(PYTHON) manage.py runserver

frontend:
	cd frontend && npm run dev
