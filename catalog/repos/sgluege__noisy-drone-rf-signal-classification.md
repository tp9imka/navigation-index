# Noisy Drone RF Signal Classification

`repo:sgluege/noisy-drone-rf-signal-classification` - <https://github.com/sgluege/Noisy-Drone-RF-Signal-Classification>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 14 | Python | GPL-3.0 | 2024-04-25 | False | research-prototype | high |

Loader and inspection scripts for a Kaggle drone RF benchmark: 16,384-sample IQ vectors and spectrograms from 6 drone remote-control transmitters plus a noise class, at SNR -20 to 30 dB in 2 dB steps.

**Why it matters:** SNR-labelled RF samples let you measure how a drone RF classifier degrades with distance and noise.

**Hackathon notes:** Kaggle download is ~26 GB (CC BY 4.0; repo code GPL-3.0). Load dataset.pt with the provided PyTorch dataloader, then train a small CNN.

**Concepts:** [Datasets and benchmarks](../concepts/datasets-benchmarks.md), [Counter-UAS and drone detection](../concepts/counter-uas.md)

**Tags:** `rf`, `snr`, `classification`, `kaggle`

**Domains:** air

## Related

- alternative_to: [RFUAV](../repos/kitoweeknd__rfuav.md)
- alternative_to: [DroneRF](../repos/al-sad__dronerf.md)

## Referenced by

- [Noisy Drone RF Signal Classification (Kaggle)](../resources/noisy-drone-rf-kaggle.md) (has_code)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
