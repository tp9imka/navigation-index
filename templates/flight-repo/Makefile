# Every target works on a clean machine with python3 only (stdlib, no venv needed).
PY    ?= python3
RUNS  ?= runs
ARENA ?= ../../samples/close-area-arena

.PHONY: help test sim arena clean

help:
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

test: ## unit tests on the mock
	$(PY) -m unittest -v test_flightloop

sim: ## fly A=>B on the mock: open, blocked, blocked with a blind planner with and without the filter
	$(PY) main.py --mock --scenario open --log $(RUNS)/open.jsonl
	$(PY) main.py --mock --scenario blocked --timeout 10 --log $(RUNS)/blocked.jsonl
	$(PY) main.py --mock --scenario blocked --timeout 10 --planner blind --log $(RUNS)/blocked-blind.jsonl
	$(PY) main.py --mock --scenario blocked --timeout 10 --planner blind --safety pass_through --log $(RUNS)/blocked-blind-nofilter.jsonl

arena: ## same loop with the hub's arena straight planner (needs the hub checkout at ARENA)
	$(PY) main.py --mock --scenario open --planner arena:straight --arena $(ARENA) --log $(RUNS)/open-arena-straight.jsonl

clean:
	rm -rf $(RUNS)
