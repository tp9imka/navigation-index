# OSNMAlib bundled Galileo I/NAV recording (current_config.sbf)

<!-- about: repo:algafix/osnma, sample:osnma-authentication -->

A real 76-minute Septentrio SBF `GALRawINAV` recording of live Galileo I/NAV pages with OSNMA, shipped inside the OSNMAlib repository together with the matching GSC public key and Merkle tree. The smallest real OSNMA data you can get: no receiver, no account, 2.6 MB. No index id for the recording itself; it is described under OSNMAlib's id.

| Field | Value |
|---|---|
| Platform | Static Septentrio receiver (static per the sample; receiver model not stated in what was read) |
| Environment | Live sky, Galileo E1 I/NAV. GST WN 1372 TOW 480090-484680 = 2025-12-12 13:21-14:37 UTC (sample's conversion, 18 leap seconds) |
| Sensors and rates | Raw I/NAV pages per SV; 5-6 of about 10 tracked SVs carried OSNMA data at a time (sample) |
| Ground truth | Not a labelled dataset. Clean signal; attacks are injected by manipulating pages (the sample's 10 scenarios) |
| Size | `custom_run/current_config.sbf` 2,614,430 B; `current_config_old_publickey1.sbf` 3,879,508 B; `OSNMA_MerkleTree.xml` 1,864 B; `OSNMA_PublicKey_2.xml` 172 B (GitHub contents API, 2026-11-06) |
| License | EUPL-1.2 (OSNMAlib repo, GitHub API). The sample keeps OSNMAlib as an external checkout and copies only derived run summaries |
| Format | Septentrio SBF, block `GALRawINAV`; keys and tree as GSC XML |
| Index | [OSNMAlib](../../catalog/repos/algafix__osnma.md), [OSNMAlib integration card](../integration-cards/algafix__osnma.md), [osnma-authentication sample](../../samples/osnma-authentication/) |

## What's in it

- PKID 2 key and the Merkle tree issued 2025-12-09, matching the recording.
- DSM IDs 0 and 11 only (KROOT); no DSM-PKR (IDs 12-15) appears in the 76 min, so a cold start with only the Merkle tree never gets a key (sample).
- A second, older recording (`current_config_old_publickey1.sbf`; by its name, from the public key 1 period; not run here).

## Download

```bash
git clone --depth 1 https://github.com/Algafix/OSNMA        # files under custom_run/
# or just the recording
curl -LO https://raw.githubusercontent.com/Algafix/OSNMA/master/custom_run/current_config.sbf
```

## Used in this repo

[samples/osnma-authentication](../../samples/osnma-authentication/) `osnma_scenarios.py --osnmalib /path/to/OSNMA --minutes 20`, run 2026-11-06 at OSNMAlib commit 25aa61de:

- 20 min of recording, 11 scenarios (clean + 10 manipulations) in about 8 s on an M-series Mac. Each scenario runs in its own process because OSNMAlib keeps config and logger in module singletons; Reed-Solomon recovery is off so a forged word is not silently repaired.
- Warm start: first ADKD0 authentication at 90 s; nominal tag lag 30 s.
- `replay_no_clock`: an 11-month-old recording authenticates perfectly on 2026-11-06, because file mode trusts the signal's own GST. Any replay demo needs an independent clock.
- Same-IOD forged data after authentication is invisible in OSNMAlib's status until the IOD changes.

## Hackathon fit

- Idea 8 (authenticate-or-alarm pipeline with Galileo OSNMA): real pages, offline, in seconds.
- Replay and time-shift attack demos on a laptop, then swap in a live u-blox `RXM-SFRBX` or GNSS-SDR feed.

## Pitfalls

- The bundled key and tree go stale at the next GSC key or tree renewal; for live use fetch both from the [GSC OSNMA page](../../catalog/resources/galileo-osnma-service-page.md).
- One 76 min static recording; no PKR broadcast in it, so cold-start behaviour cannot be shown with it.
- Python 3.10-3.12 for OSNMAlib per the sample.

## Sources

- GitHub contents API for `Algafix/OSNMA/custom_run` and repo licence, 2026-11-06
- samples/osnma-authentication/README.md
