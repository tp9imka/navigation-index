# ADS-B Exchange free monthly sample (readsb-hist)

<!-- about: res:adsbexchange-monthly-samples, sample:osint-jamming-map, repo:wiedehopf/readsb, res:gpsjam-org -->

ADS-B Exchange publishes its complete global feed free of charge for the 1st day of each month: `readsb-hist` snapshots, one gzipped `aircraft.json` per 5 s, with each aircraft's NACp / NIC quality fields and MLAT flags. That is enough to rebuild a GPSJam-style interference map for any past 1st-of-month. No login. No index id of its own; the marker names the sample, the decoder whose JSON format it uses, and GPSJam.

| Field | Value |
|---|---|
| Platform | Crowd-sourced ground ADS-B / MLAT receivers (readsb aggregator) |
| Environment | Global, wherever receivers and traffic exist; sparse over Russia, oceans, Africa |
| Sensors and rates | Global snapshot every 5 s (sample's `SNAPSHOT_STEP_S`); per aircraft: position, altitude, `nac_p`, `nic`, `gpsOkBefore`, `mlat` field list, etc. (readsb JSON) |
| Ground truth | None. NACp is the aircraft's own estimate of its position accuracy; MLAT positions are independent of the aircraft's GNSS |
| Size | One snapshot `2026/10/01/045100Z.json.gz` = 4,962,761 B (GET, 2026-11-06; HEAD returns no length). The sample's 121 snapshots (2 h at 60 s) were about 600-750 MB to download |
| License | "Complete data from the 1st of each month are made available free of charge" (sample page); no open licence named, site footer says all rights reserved; ADS-B Exchange Terms of Use and Acceptable Use Policy apply. Check before redistributing raw snapshots or using commercially |
| Format | gzip JSON, readsb `aircraft.json` schema |
| Index | [osint-jamming-map sample](../../samples/osint-jamming-map/), [readsb](../../catalog/repos/wiedehopf__readsb.md), [GPSJam](../../catalog/resources/gpsjam-org.md) |

## Download

```bash
# https://samples.adsbexchange.com/readsb-hist/YYYY/MM/DD/HHMMSSZ.json.gz, DD = 01 only
curl -O https://samples.adsbexchange.com/readsb-hist/2026/10/01/045100Z.json.gz
# what the sample does: 2 h window at 60 s, filtered to a bbox and cached
python3 samples/osint-jamming-map/adsb_hexmap.py
```

`2026/11/02/...` returned HTTP 404 on 2026-11-06, as expected: only the 1st is published. The 1st of a month appeared about 1.5 days later (`last-modified` 2026-10-02 20:21 for 10-01, 2026-11-02 20:23 for 11-01).

## Used in this repo

[samples/osint-jamming-map](../../samples/osint-jamming-map/) `adsb_hexmap.py`, run 2026-11-06 for 2026-10-01 03:51-05:51 UTC over the SE Baltic (18-25 E, 53.5-57 N):

- 121 snapshots, 129 aircraft with a usable quality field, 110 with NACp < 8 or `gpsOkBefore`; 64 red H3 res-4 hexes. Control NL / DE (13 snapshots): 19 of 879 degraded.
- 105 of the 110 degraded aircraft were at some point MLAT-positioned: the aircraft has no GNSS position to send, so the ground network multilaterates it.
- Commits only derived aggregates and about 2,300 position reports, because of the licence terms.

## Loading and tooling

- Python stdlib `gzip` + `json`; H3 for hexes. GPSJam formula `(bad - 1) / total` with a 3-aircraft minimum, as in the sample.
- [ADSBCOT](../../catalog/repos/snstac__adsbcot.md) pushes live readsb / dump1090 JSON into TAK; [traffic](../../catalog/repos/xoolive__traffic.md) for trajectory work.

## Hackathon fit

- Idea 2 (ADS-B-derived interference map for your region): a past window for any region with traffic, free, no account.
- Context layer next to a GNSS interference monitor (idea 1) or a Sentinel-1 RFI layer.

## Pitfalls

- Only the 1st of each month. Pick event dates or satellite passes around that.
- Each snapshot is global (about 5 MB gzipped); 2 h at 60 s is roughly 0.6-0.75 GB even if you keep a small bbox. Filter while downloading.
- NACp says "degraded", not why: jamming, spoofing, avionics fault, old transponder. Under spoofing the reported position is itself false and lands in the wrong hex.
- No-data hexes are not clean hexes.
- Other routes checked by the sample: OpenSky historical with NACp needs an approved research account; airplanes.live and the ADS-B Exchange API are live only.

## Sources

- GET / HEAD on `samples.adsbexchange.com` snapshot URLs, 2026-11-06
- samples/osint-jamming-map/README.md and `adsb_hexmap.py`
