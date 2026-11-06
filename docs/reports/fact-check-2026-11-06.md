# Fact check - 2026-11-06

This was a sampled check, not full verification. The mechanical pass covered every repo
record. The deep pass covered 60 repos and 116 resources, out of 588 repo records and 433
resource records. `data/repos/gap-fill.json` and `data/resources/gap-fill.json` were
excluded: another agent was writing them while this check ran.

Scripts and raw outputs are in the session scratchpad, under `factcheck/`:
`mechanical.py`, `sample.py`, `arxiv_check.py`, `patch.py`, `applied.log`,
`mechanical-before.tsv` / `mechanical-after.tsv` and `arxiv_results.json`.

## Method

1. **Mechanical, all repo records (588 records, 586 with GitHub metadata).** A stdlib
   script compared each record with `data/github_meta.json` on four things:
   - maturity vs `archived` and `pushed_at`, using the three rules in the brief;
   - `language` vs the GitHub primary language;
   - summary vs GitHub description, using a word-overlap heuristic;
   - year claims in prose ("dormant since 2022", "last updated 2024") vs `pushed_at`.

   I reviewed every flag by hand. For the language flags I pulled the per-language byte
   counts (`gh api repos/<o>/<n>/languages`).
2. **Deep repo sample (60 repos).** I picked 40 at random from the 169 `hackathon_fit: high`
   records and 20 at random from the rest, with a fixed seed (`sample.py`). For each one I
   read `summary`, `why_it_matters` and `hackathon_notes` against the head of the live
   README. I opened the docs or repo tree where a claim was specific (install command,
   bundled tools).
3. **Resources.**
   - **All 74 arXiv-linked resources, automatically.** Title similarity, author surname
     overlap and year, checked against the `citation_*` meta tags on arxiv.org/abs.
   - **42 non-arXiv resources, by hand.** A random sample of papers, standards, talks,
     reports, books and courses, checked against the publisher page (curl, WebFetch) or
     a web search. A few were checked against well-established knowledge.

## Results by category

| Check | Checked | Flagged | Real errors | Fixed |
|---|---|---|---|---|
| Maturity vs metadata | 586 | 3 | 2 | 2 |
| Language vs GitHub | 586 | 15 | 4 ids (5 records) | 4 ids (5 records) |
| Summary vs description (heuristic) | 586 | 7 | 0 | 0 |
| Year claims in prose ("since YYYY") | 57 claims | 0 | 0 | 0 |
| Deep repo sample (README) | 60 | - | 5 | 5 |
| arXiv resources (automatic) | 74 | 8 | 4 (1 truncated title, 3 vague/invented author attributions) | 4 |
| Non-arXiv resource sample | 42 | - | 3 (1 wrong title, 1 wrong year, 1 author formatting) | 3 |

**Error rates.**
- Deep repo sample: 5/60 = **8.3%** of records had at least one wrong or outdated claim.
  - 2 were wrong when written: tetra3 install, gps-measurement-tools contents.
  - 3 were overtaken by upstream changes in 2026: OpenSky auth, the mavsdk PyPI rename, the mgrs backend.
- Resources:
  - arXiv: 0/74 wrong titles or years. 1 title truncated. Several author fields hold a
    team or org name instead of people.
  - Non-arXiv: 2/42 = **4.8%** substantive errors (GAO title, OSNMA year), plus 1
    formatting fix.
- No fabricated record turned up. Every sampled repo and resource exists.

## Corrections (id: what changed)

Maturity (check 1):
- `repo:unmannedlab/rellis-3d`: maturity production => archived (last push 2022-11). Notes: added "Unmaintained since 2022; the data itself is static and still usable."
- `repo:williamwenda/uwb_tdoa_dataset`: maturity production => archived (last push 2021-04). Notes: added "Unmaintained since 2021; ..." in the same form.

Language (check 1, confirmed with the per-language byte counts):
- `repo:signalk/signalk-to-nmea0183`: JavaScript => TypeScript.
- `repo:goblimey/ntripcaster`: Dockerfile => C (the repo vendors the BKG caster C source).
- `repo:robotics-upo/gaussian-rio`: C++ => Python (Python-dominant, plus CUDA/C++).
- `repo:sxjack/uav_electronic_ids`: C++ => C (fixed in both autopilots and domains-swarm).

Deep repo sample:
- `repo:google/gps-measurement-tools` (gnss lane): summary claimed "a rinex converter". The repo has a RINEX nav reader and NMEA utilities, not a converter.
- `repo:hobuinc/mgrs`: summary said it wraps the GeoTrans C code. It now uses a Rust port of GEOTRANS 3.10 behind a pybind11 extension. Notes: added that since 1.6.0 inverse conversion returns the cell centre, not the SW corner.
- `repo:openskynetwork/opensky-api`: notes now mention that basic auth was dropped in March 2026 in favour of OAuth2 client credentials.
- `repo:mavlink/mavsdk-python`: notes said `pip install mavsdk`. The package is now `mavsdk-grpc`, imported as `mavsdk_grpc`. The PyPI name `mavsdk` now means the native binding, which has a different API.
- `repo:esa/tetra3`: notes said `pip install`. tetra3 is not on PyPI; the notes now use `pip install git+https://github.com/esa/tetra3.git`.

Resources:
- `res:arxiv-multi-robot-triage-platform`: title completed ("... Combining Onboard Sensing and Foundation Models"). Authors set to the first four arXiv authors, et al.
- `res:protecting-gnss-intentional-interference-arxiv`: authors "Academic GNSS security community" => the five arXiv authors (Elango, Al-Tahmeesschi, Saukkoriipi, Malmivirta, Ruotsalainen).
- `res:wildnav-gnss-free-uav-localization-2022`: authors "TIERS lab" => Gurgu, Peña Queralta, Westerlund.
- `res:gao-21-320sp-gps-alternatives`: the title was paraphrased. Set to the official one: "Defense Navigation Capabilities - DOD Is Developing Positioning, Navigation, and Timing Technologies to Complement GPS".
- `res:galileo-osnma-receiver-guidelines`: year 2023 => 2024. Issue 1.3 is dated January 2024; the gnss-lane twin already had 2024.
- `res:rados-2024-jamming-spoofing-detection-review`: one comma-joined author string => three entries with the correct diacritics (Radoš, Brkić, Begušić).

## Reviewed and kept

- `repo:microsoft/airsim`: kept as `archived`, although the mechanical rule flags it.
  Upstream is not archived and was pushed 2026-09-15, but recent commits are only CI action
  pinning and README edits. Development wound down years ago, so `archived` reflects
  reality better than the repo flag.
- Language flags kept as-is, because GitHub's linguist misreads these:
  - `borglab/gtsam`: GitHub says Jupyter Notebook; the code is C++.
  - `dronecan/libcanard`: C, with C++ tests.
  - `mavlink/mavlink-devguide`: Markdown.
  - `px4/flight_review`: GitHub says JavaScript (vendored JS); it is a Python/Bokeh app.
  - `jaffarrell/av-matlab-sw`: GitHub says TeX; the code is MATLAB.
  - The rest are C vs C++ splits caused by vendored RTKLIB or similar.
- Summary-overlap flags were all false positives. The summaries are paraphrases that match
  the description in substance.
- Team or org author fields (CERBERUS, CoSTAR, DAF-MIT AI Accelerator) are honest
  attributions, so I left them.

## Duplicates found (not fixed - an editorial call, not a fact error)

21 URLs appear under two or three different resource ids across lanes. Examples:
- the OPSGROUP spoofing report;
- Dellaert & Kaess "Factor Graphs for Robot Perception";
- the MagNav challenge paper (3 ids);
- the OSNMA SIS ICD and Receiver Guidelines;
- the Kaggle GSDC 2022 and 2023 competitions;
- Navipedia;
- the Solà ESKF notes;
- the SLAM Handbook;
- the Swarm-SLAM paper.

Twins can drift apart: before this check, the two OSNMA guideline records disagreed on the
year. The builder should merge them or add a duplicate-URL lint.

## Could not verify

- `res:ion-webinar-akos` (2022) and `res:ion-webinar-shamaei-kassas` (2019): the ION
  webinar pages need sign-in. The underlying papers exist (NAVIGATION 2022 and 2018,
  matching authors). The webinar dates are plausible but unconfirmed.
- `res:spire-gnss-interference-russia-kaliningrad` and `res:c4ads-above-us-only-stars`:
  both pages sit behind a Cloudflare challenge. C4ADS 2019 matches the known publication
  date. The Spire title and year are unchecked.
- `res:dodd-4650-05-pnt` (year 2023): the document is DoDD 4650.05 of June 9, 2016, with
  Change 3 of April 25, 2023. 2023 is defensible, but it is the change date, not the
  issuance date.
- `repo:gitlab.com/gpsd/gpsd` and `repo:gitlab.com/radionavlab/public/ut-starlink-signal-simulator`:
  no GitHub metadata, so they were not covered by the mechanical checks.

## Residual risk

- About 90% of repo records and about 73% of resource records got no README or source
  read beyond the mechanical checks.
- At the sampled rates, expect roughly 40-50 more repo records with a stale or wrong
  detail. They would cluster in install commands, packaging and auth gotchas in
  `hackathon_notes`, which age fastest.
- Expect 10-15 resources with a title, year or author slip, concentrated in standards and
  reports with revisions or reissues.
- Core identity claims held up across the sample: what a repo is, its venue and year.
- `why_it_matters` claims are opinions and were not scored.
