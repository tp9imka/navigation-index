# File-based GNSS signal chain. Nothing here transmits RF.
IMAGE ?= gnss-signal-chain
VOL ?= gnss-signal-chain-work

.PHONY: image run score clean-volume check
image:
	docker build -t $(IMAGE) docker/

run: image
	./run.sh

ATTACK_T ?= 75
DRAG_ON ?= 60
SCENARIOS ?= clean overpower jamspoof dragoff

# re-score existing out/ without regenerating IQ (host python3, stdlib only).
# Two passes per scenario: constant-velocity prior (.score.*) and a static velocity reference
# (.score-ref.*, --ref-vel 0,0 = the platform knows it is not moving).
score:
	for s in $(SCENARIOS); do \
	  case $$s in clean) at=;; dragoff) at="--attack-t $(DRAG_ON)";; *) at="--attack-t $(ATTACK_T)";; esac; \
	  python3 score_scenario.py out/$$s.epochs.jsonl --power-proxy out/$$s.power.csv $$at \
	    --rtklib-pos out/$$s.rtklib.pos --json-out out/$$s.score.json > out/$$s.score.txt; \
	  python3 score_scenario.py out/$$s.epochs.jsonl --power-proxy out/$$s.power.csv $$at --ref-vel 0,0 \
	    --json-out out/$$s.score-ref.json > out/$$s.score-ref.txt; \
	  echo "== $$s"; tail -3 out/$$s.score.txt; tail -2 out/$$s.score-ref.txt; done

check:
	bash -n run.sh pipeline.sh
	python3 -m py_compile mix_iq.py spoof_trajectory.py extract_epochs.py score_scenario.py

clean-volume:
	docker volume rm $(VOL)
