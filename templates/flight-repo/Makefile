# test, sim, arena: python3 only (stdlib, no venv needed).
# first-flight: builds the arena's own venv (numpy, scipy, matplotlib) with uv on first use.
PY     ?= python3
RUNS   ?= runs
ARENA  ?= ../../samples/close-area-arena
SAFETY ?= ../../samples/close-area-safety-filter
VPY    ?= $(ARENA)/.venv/bin/python
FLIGHT ?= --adapter arena:random:0 --planner arena:astar_esdf --safety arm:F2
FAULT  ?=

.PHONY: help test sim arena venv first-flight first-flight-jump clean

help:
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-18s %s\n", $$1, $$2}'

test: ## unit tests on the mock
	$(PY) -m unittest -v test_flightloop
	$(PY) -c "import flightloop.arena_adapter, flightloop.safety_shim; print('arena_adapter, safety_shim import without numpy: ok')"
	@if [ -x $(VPY) ]; then \
	  $(VPY) main.py $(FLIGHT) --arena $(ARENA) --safety-dir $(SAFETY) --timeout 3 --log $(RUNS)/smoke_arena.jsonl \
	  && $(VPY) $(ARENA)/score_log.py $(RUNS)/smoke_arena.jsonl > /dev/null && echo "arena smoke (3 s flight, scored): ok"; \
	else echo "skip arena smoke: no $(VPY) (run make venv)"; fi

sim: ## fly A=>B on the mock: open, blocked, blocked with a blind planner with and without the filter
	$(PY) main.py --mock --scenario open --log $(RUNS)/open.jsonl
	$(PY) main.py --mock --scenario blocked --timeout 10 --log $(RUNS)/blocked.jsonl
	$(PY) main.py --mock --scenario blocked --timeout 10 --planner blind --log $(RUNS)/blocked-blind.jsonl
	$(PY) main.py --mock --scenario blocked --timeout 10 --planner blind --safety pass_through --log $(RUNS)/blocked-blind-nofilter.jsonl

arena: ## same loop with the hub's arena straight planner (needs the hub checkout at ARENA)
	$(PY) main.py --mock --scenario open --planner arena:straight --arena $(ARENA) --log $(RUNS)/open-arena-straight.jsonl

$(VPY):
	uv venv $(ARENA)/.venv && uv pip install --python $(ARENA)/.venv -r $(ARENA)/requirements.txt

venv: $(VPY) ## arena venv (numpy, scipy, matplotlib; also covers the safety-filter sample)

first-flight: $(VPY) ## arena:random:0 + astar_esdf + F2 through this loop, then score_log.py => results/first_flight.png
	$(VPY) main.py $(FLIGHT) $(FAULT) --arena $(ARENA) --safety-dir $(SAFETY) --log results/first_flight.jsonl
	$(VPY) $(ARENA)/score_log.py results/first_flight.jsonl --plot results/first_flight.png --json results/first_flight_score.json

first-flight-jump: $(VPY) ## same with the arena estimator's jump fault => results/first_flight_jump.png
	$(VPY) main.py $(FLIGHT) --fault jump --arena $(ARENA) --safety-dir $(SAFETY) --log results/first_flight_jump.jsonl
	$(VPY) $(ARENA)/score_log.py results/first_flight_jump.jsonl --plot results/first_flight_jump.png --json results/first_flight_jump_score.json

clean:
	rm -rf $(RUNS)
