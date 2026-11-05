# Kubo: comandos de desenvolvimento. O backend usa um venv isolado em apps/backend/.venv.
# Funciona em cmd.exe e sh. pnpm roda via npx para dispensar instalação global.

BACKEND := apps/backend
ifeq ($(OS),Windows_NT)
PY := ".venv/Scripts/python.exe"
else
PY := .venv/bin/python
endif
PNPM ?= npx --yes pnpm@9.15.9

.PHONY: install db backend worker scheduler frontend types migrate makemigrations test test-backend test-web lint fmt build

install:
	cd $(BACKEND) && uv venv --python 3.12 .venv && uv pip install --python $(PY) -e ".[dev]"
	$(PNPM) install

# Postgres local sem Docker, instalado no venv (porta 5433). Fica em primeiro plano.
db:
	cd $(BACKEND) && $(PY) scripts/dev_db.py

backend:
	cd $(BACKEND) && $(PY) manage.py runserver

worker:
	cd $(BACKEND) && $(PY) manage.py run_generation_worker

scheduler:
	cd $(BACKEND) && $(PY) manage.py run_scheduler

frontend:
	$(PNPM) --filter @kubo/consumer dev

migrate:
	cd $(BACKEND) && $(PY) manage.py migrate

makemigrations:
	cd $(BACKEND) && $(PY) manage.py makemigrations

# Contrato: OpenAPI do backend -> schema.yaml -> tipos do frontend.
types:
	cd $(BACKEND) && $(PY) manage.py spectacular --file ../../packages/api-types/schema.yaml --validate
	$(PNPM) --filter @kubo/api-types generate

test: test-backend test-web

test-backend:
	cd $(BACKEND) && $(PY) -m pytest

test-web:
	$(PNPM) -r test

lint:
	cd $(BACKEND) && $(PY) -m ruff check .
	$(PNPM) -r lint
	$(PNPM) -r typecheck

fmt:
	cd $(BACKEND) && $(PY) -m ruff check --fix . && $(PY) -m ruff format .
	$(PNPM) format

build:
	$(PNPM) --filter @kubo/consumer build
