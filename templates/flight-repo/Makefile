# test, sim, arena: python3 only (stdlib, no venv needed).
# first-flight*: builds ./.venv (numpy, scipy, matplotlib) with uv on first use, inside this folder.
# Copied out of the hub: pass the hub sample paths, e.g.
#   make first-flight ARENA=/path/to/hub/samples/close-area-arena SAFETY=/path/to/hub/samples/close-area-safety-filter
# Any benchmark planner, in a world file (close-area-world/1, e.g. a playground preset):
#   make first-flight PLANNER=bench:dstar_lite WORLD=../../site/playground/presets/narrow_gap_0.json
#   make bench-list      # the bench: ids, which read the world, which loaded
PY     ?= python3
RUNS   ?= runs
HUB    ?= ../..
ARENA  ?= $(HUB)/samples/close-area-arena
SAFETY ?= $(HUB)/samples/close-area-safety-filter
RELOC  ?= $(HUB)/samples/close-area-relocalize
BENCH  ?= $(HUB)/samples/close-area-benchmark
VENV   ?= .venv
VPY    ?= $(VENV)/bin/python
PLANNER ?= arena:astar_esdf
WORLD  ?=
ADAPTER ?= $(if $(WORLD),world:$(WORLD),arena:random:0)
ARM    ?= F2
FLIGHT ?= --adapter $(ADAPTER) --planner $(PLANNER) --safety arm:$(ARM)
FAULT  ?=
DIRS    = --arena $(ARENA) --safety-dir $(SAFETY) --bench-dir $(BENCH)
# results/<OUT>.{jsonl,png} and <OUT>_score.json; the default flight keeps results/first_flight.*
OUT    ?= $(if $(WORLD)$(filter-out arena:astar_esdf,$(PLANNER)),first_flight_$(subst :,_,$(PLANNER))$(if $(WORLD),_$(basename $(notdir $(WORLD)))),first_flight)

# Stop with a clear message before anything is created if a hub path is wrong.
define need
@if [ ! -f "$(1)" ]; then \
	  echo "error: $(1) not found."; \
	  echo "This target needs the navigation-index hub samples. Set the paths, e.g.:"; \
	  echo "  make $(or $(MAKECMDGOALS),first-flight) ARENA=/path/to/hub/samples/close-area-arena SAFETY=/path/to/hub/samples/close-area-safety-filter RELOC=/path/to/hub/samples/close-area-relocalize"; \
	  echo "(or HUB=/path/to/hub for all of them; bench: planners also need BENCH=/path/to/hub/samples/close-area-benchmark)"; \
	  exit 2; fi
endef

.PHONY: help test sim arena venv bench-list first-flight first-flight-jump first-flight-reloc clean

help:
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-20s %s\n", $$1, $$2}'

test: ## unit tests on the mock, stdlib import check, arena smoke if the venv and arena exist
	$(PY) -m unittest -v test_flightloop
	@if [ -x $(VPY) ] && [ -f $(BENCH)/bench.py ]; then \
	  BENCH_DIR=$(BENCH) ARENA_DIR=$(ARENA) $(VPY) -m unittest -v test_flightloop.BenchPlanner; \
	else echo "skip bench: loading test under the venv: needs $(VPY) (make venv) and BENCH=$(BENCH)"; fi
	$(PY) -c "import flightloop.arena_adapter, flightloop.safety_shim, flightloop.reloc_shim, flightloop.bench_planner; print('arena_adapter, safety_shim, reloc_shim, bench_planner import without numpy: ok')"
	@if [ -x $(VPY) ] && [ -f $(ARENA)/__init__.py ] && [ -f $(SAFETY)/filters.py ]; then \
	  $(VPY) main.py $(FLIGHT) $(DIRS) --timeout 3 --log $(RUNS)/smoke_arena.jsonl \
	  && $(VPY) $(ARENA)/score_log.py $(RUNS)/smoke_arena.jsonl > /dev/null && echo "arena smoke (3 s flight, scored): ok"; \
	else echo "skip arena smoke: needs $(VPY) (make venv) and the hub at ARENA=$(ARENA), SAFETY=$(SAFETY)"; fi

sim: ## fly A=>B on the mock: open, blocked, blocked with a blind planner with and without the filter
	$(PY) main.py --mock --scenario open --log $(RUNS)/open.jsonl
	$(PY) main.py --mock --scenario blocked --timeout 10 --log $(RUNS)/blocked.jsonl
	$(PY) main.py --mock --scenario blocked --timeout 10 --planner blind --log $(RUNS)/blocked-blind.jsonl
	$(PY) main.py --mock --scenario blocked --timeout 10 --planner blind --safety pass_through --log $(RUNS)/blocked-blind-nofilter.jsonl

arena: ## same loop with the hub's arena straight planner (needs the hub checkout at ARENA)
	$(call need,$(ARENA)/__init__.py)
	$(PY) main.py --mock --scenario open --planner arena:straight --arena $(ARENA) --log $(RUNS)/open-arena-straight.jsonl

$(VPY):
	$(call need,$(ARENA)/requirements.txt)
	uv venv $(VENV) && uv pip install --python $(VENV) -r $(ARENA)/requirements.txt

venv: $(VPY) ## ./.venv with the arena requirements (numpy, scipy, matplotlib; covers safety filter and relocalizer)

bench-list: $(VPY) ## the close-area-benchmark planner ids for PLANNER=bench:<id>
	$(call need,$(BENCH)/bench.py)
	$(VPY) main.py --planner bench:list --bench-dir $(BENCH)

first-flight: $(VPY) ## arena:random:0 + astar_esdf + F2 (or PLANNER=, WORLD=, ARM=), scored => results/$(OUT).png
	$(call need,$(SAFETY)/filters.py)
	$(if $(filter bench:%,$(PLANNER)),$(call need,$(BENCH)/bench.py))
	$(if $(WORLD),$(call need,$(WORLD)))
	$(VPY) main.py $(FLIGHT) $(FAULT) $(DIRS) --log results/$(OUT).jsonl
	$(VPY) $(ARENA)/score_log.py results/$(OUT).jsonl --plot results/$(OUT).png --json results/$(OUT)_score.json

first-flight-jump: $(VPY) ## same with the arena estimator's jump fault => results/first_flight_jump.png
	$(call need,$(SAFETY)/filters.py)
	$(VPY) main.py $(FLIGHT) --fault jump $(DIRS) --log results/first_flight_jump.jsonl
	$(VPY) $(ARENA)/score_log.py results/first_flight_jump.jsonl --plot results/first_flight_jump.png --json results/first_flight_jump_score.json

first-flight-reloc: $(VPY) ## jump fault + relocalization (multi_ig) => results/first_flight_reloc*.{jsonl,png,json}
	$(call need,$(SAFETY)/filters.py)
	$(call need,$(RELOC)/disambiguate.py)
	$(VPY) main.py $(FLIGHT) --fault jump --reloc --reloc-dir $(RELOC) $(DIRS) --log results/first_flight_reloc.jsonl --odom results/first_flight_reloc_odometry.jsonl
	$(VPY) $(ARENA)/score_log.py results/first_flight_reloc.jsonl --plot results/first_flight_reloc.png --json results/first_flight_reloc_score.json

clean:
	rm -rf $(RUNS)
