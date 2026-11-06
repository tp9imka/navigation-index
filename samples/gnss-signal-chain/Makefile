# File-based GNSS signal chain. Nothing here transmits RF.
IMAGE ?= gnss-signal-chain
VOL ?= gnss-signal-chain-work

.PHONY: image run score clean-volume check
image:
	docker build -t $(IMAGE) docker/

run: image
	./run.sh

# re-score existing out/ without regenerating IQ (host python3, stdlib only)
score:
	for s in clean overpower jamspoof dragoff; do \
	  python3 score_scenario.py out/$$s.epochs.jsonl --power-proxy out/$$s.power.csv \
	    --rtklib-pos out/$$s.rtklib.pos --json-out out/$$s.score.json | tee out/$$s.score.txt; done

check:
	bash -n run.sh pipeline.sh
	python3 -m py_compile mix_iq.py spoof_trajectory.py extract_epochs.py score_scenario.py

clean-volume:
	docker volume rm $(VOL)
