# Every target works on a clean machine with python3 only; docker targets need Docker.
PY      ?= python3
RUNS    ?= runs
ORIGIN  ?= 59.0,10.0
export PYTHONPATH := src

.PHONY: help setup test sim demo eval up down clean

help:
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

setup: ## create .venv (stdlib core needs nothing; add deps to pyproject extras)
	$(PY) -m venv .venv
	@echo "activate: . .venv/bin/activate"

test: ## unit tests
	$(PY) -m unittest discover -s tests -v

sim: ## run every synthetic scenario, with and without integrity
	@mkdir -p $(RUNS)
	for s in clean jam spoof; do \
	  $(PY) -m navapp --scenario $$s --origin $(ORIGIN) --out $(RUNS)/$$s.jsonl; \
	  $(PY) -m navapp --scenario $$s --origin $(ORIGIN) --no-integrity --out $(RUNS)/$$s-baseline.jsonl; \
	done

demo: ## spoof scenario streamed as CoT to a local TAK input and STATUSTEXT to a GCS port
	$(PY) -m navapp --scenario spoof --origin $(ORIGIN) --out $(RUNS)/demo.jsonl \
	  --cot-udp 127.0.0.1:6969 --mavlink-udp 127.0.0.1:14550

eval: sim ## metrics table for the README results section
	$(PY) eval/metrics.py $(RUNS)/clean*.jsonl $(RUNS)/jam*.jsonl $(RUNS)/spoof*.jsonl | tee $(RUNS)/results.md

up: ## docker compose stack (sim + app + tak)
	docker compose up -d

down:
	docker compose down

clean:
	rm -rf $(RUNS) .venv build *.egg-info src/*.egg-info
