# Search ranking: legacy term counting vs BM25F

Date: 2026-11-06. Scope: `tools/query.py search`, the MCP `search` tool (`tools/mcp_server.py`, which calls `query.search`) and the web UI (`site/app.js`).

## Problem

The old ranker summed `field_weight * substring_count` per query term. Common words won on volume: `visual geolocalization` put `res:orb-slam3-campos-2020` first because "visual" shows up many times in it, and no geolocalization record made the top 10. With the new ranker that paper is at rank 125 and the top 10 is all image-to-map localization work.

## Evaluation set

`tools/search_queries.json`: 30 queries, each with 4-6 relevant ids, split into 20 train and 10 holdout (`split` field). Run it with `python3 tools/search_eval.py` (add `-v` for per-query rows).

How the judgments were made: for each topic I grepped `index/records.jsonl` with a topic regex to list candidates, read their summaries and picked the clearly on-topic ones. I never looked at either ranker's output when choosing. Caveats:

- Relevance is binary and was judged by one person (the agent).
- The lists are incomplete on purpose (3-6 per query). Many unjudged results are relevant too: for `visual geolocalization` every top-10 hit is on topic, but only 4 of the 10 are in the judged list. So absolute numbers understate both rankers. The comparison between them is what matters.
- Candidates came from keyword grep, which favours records that use the query words literally. That may help lexical rankers a bit.
- With 10 holdout queries, a single query moving one rank shifts holdout nDCG by about 0.01-0.03. Treat differences under ~0.02 as noise.

Metrics: MRR (first relevant hit at any depth), nDCG@10 (binary gains), recall@10 (relevant ids in top 10 / min(#relevant, 10)).

## Results

| ranker | split | n | MRR | nDCG@10 | R@10 |
|---|---|---|---|---|---|
| legacy (term counts) | train | 20 | 0.702 | 0.572 | 0.613 |
| legacy (term counts) | holdout | 10 | 0.506 | 0.433 | 0.490 |
| legacy (term counts) | all | 30 | 0.636 | 0.526 | 0.572 |
| BM25F v0 (initial params, before tuning) | train | 20 | 0.820 | 0.724 | 0.805 |
| BM25F v0 (initial params, before tuning) | holdout | 10 | 0.766 | 0.660 | 0.707 |
| **BM25F shipped** | train | 20 | 0.892 | 0.782 | 0.842 |
| **BM25F shipped** | holdout | 10 | 0.833 | 0.717 | 0.797 |
| **BM25F shipped** | all | 30 | 0.872 | 0.760 | 0.827 |

Holdout nDCG@10 goes from 0.433 to 0.717. Per query, 27 of 30 improve or stay level. Three get slightly worse: `android raw gnss` (holdout, nDCG 0.84 => 0.74, MRR 1.0 => 0.5), `osnma` (holdout, 0.89 => 0.82) and `ntrip caster` (train, 0.95 => 0.91). In each of the three, the top results are still on-topic records.

## What the ranker does

The Python reference is `Ranker` in `tools/query.py`. `site/app.js` has a line-for-line port between the `// ---- ranker begin` and `// ---- ranker end` markers.

- **Tokenizer:** lowercase, then `isation` => `ization` and `geo-localization` / `geo localisation` => `geolocalization`. It splits on non-alphanumerics, drops a short stopword list and strips plurals (`-ies` => `-y`, trailing `-s` except `-ss/-us/-is`). It folds synonyms into one token: `gps` => `gnss`; `drone`, `uas`, `suas`, `quadcopter`, `quadrotor`, `multirotor` => `uav`; `ladar` => `lidar`.
- **BM25F** (k1 = 1.2) over 10 fields with per-field weight and length normalization b:
  - `name` (name/title) 4.0 / 0.3
  - `tags` 1.5 / 0.3
  - `concepts` (names of the record's concepts) 1.5 / 0
  - `summary` 1.5 / 0.6
  - `why_it_matters` 0.7 / 0.6
  - `hackathon_notes` 0.5 / 0.6
  - `key_takeaways` 0.7 / 0.6
  - `language` 1.0 / 0
  - `kind` 1.0 / 0
  - `deep` 1.0 / 0.75

  IDF is computed over all 1366 index records. A record must match at least one query term to be returned.
- **Deep-dive text:** the first 1500 chars of plain text of each attached doc in `deep_dives`, using the same `md_plain` and cut as `build.write_site`, so Python and the web UI index identical text. Hub docs attached to more than 4 records (indexes, READMEs) are skipped as too generic.
- **Concept boost:** a concept fires when the IDF-weighted share of the query covered by its name and id slug is at least 0.5. Its members (and the concept node itself) get `2.5 * share`, taking the max over the record's concepts.
- **Priors:** hackathon fit high +0.4 and medium +0.15. A sample whose `verified` text says it was run gets +0.4. The priors are only added to records that already match a term.
- **Ties:** broken by score rounded to 1e-6, then stars, then id. The rounding keeps ordering identical between Python and JS.
- **Filters:** `--kind/--fit/--domain/--concept` and MCP filters are applied after ranking, so corpus statistics do not depend on the filter.

No build change was needed. `site/data/index.json` already carries every field the JS ranker uses (`n g c s w h kt lg k dd f vs st`, plus doc `b`/`p`).

## Tuning and ablation

The train split was the only input to tuning. The v0 parameters were set by hand before any measurement. I then ran a grid on train nDCG@10 over concept boost weight, phrase bonus weight, coverage factor, deep-text weight, name weight and tag weight, and shipped the best train configuration. I looked at the holdout numbers only after choosing.

Two features from the original design were implemented, measured and removed, because train scored best with them off:

- **Phrase/bigram bonus.** At weights 0.1-0.6 (bonus when adjacent query terms appear adjacent in name/tags/concepts/summary), train nDCG@10 was 0.751-0.757 vs 0.764 at 0.
- **Coverage factor.** A score multiplier for the IDF share of query terms matched. Train nDCG was best at 1.0, i.e. off. BM25's IDF already handles the "common word wins" failure.

Ablation of the shipped ranker (cells are MRR / nDCG@10 / R@10):

| variant | train | holdout | all |
|---|---|---|---|
| shipped | 0.892 / 0.782 / 0.842 | 0.833 / 0.717 / 0.797 | 0.872 / 0.760 / 0.827 |
| no concept boost | 0.892 / 0.778 / 0.833 | 0.833 / 0.717 / 0.797 | 0.872 / 0.758 / 0.821 |
| no concept-name field | 0.929 / 0.747 / 0.762 | 0.783 / 0.699 / 0.797 | 0.880 / 0.731 / 0.773 |
| no concept field and no boost | 0.928 / 0.742 / 0.753 | 0.783 / 0.690 / 0.780 | 0.880 / 0.724 / 0.762 |
| no deep-dive text | 0.867 / 0.766 / 0.825 | 0.833 / 0.706 / 0.797 | 0.856 / 0.746 / 0.816 |
| no priors | 0.875 / 0.751 / 0.792 | 0.925 / 0.704 / 0.743 | 0.892 / 0.735 / 0.776 |
| no synonyms / normalization | 0.863 / 0.760 / 0.817 | 0.833 / 0.698 / 0.777 | 0.853 / 0.740 / 0.803 |
| no language/kind fields | 0.892 / 0.784 / 0.842 | 0.833 / 0.704 / 0.780 | 0.872 / 0.758 / 0.821 |

How to read it:

- Most of the concept signal comes from indexing concept names as a field. The explicit boost on top changes only 1 of 30 top-10 lists. It is kept because it is cheap and helps short queries that name a concept exactly.
- Priors trade MRR for recall: removing them raises holdout MRR but lowers nDCG and recall.
- All other deltas are within the noise band stated above.

## Python / JS parity

`python3 tools/search_eval.py --parity` loads `site/data/index.json`, runs the `app.js` ranker block under node (`vm`), drops `doc:` hits (the web UI also ranks deep-dive docs as separate results, scored against the same corpus stats), and compares the top 10 with `query.search`.

- **Result:** 30/30 eval queries have identical ids and scores within 1e-6.
- **Wider ad-hoc check:** 56/56 for the 46 concept names plus 10 odd queries (`c-uas`, `ORB-SLAM3`, Cyrillic, stopword-only, ...).
- **Negative control:** changing one JS constant made 25 of 30 queries mismatch, so the check can fail.

Not verified: the ranker was not exercised in a browser. Only the ranker block was run under node. The integration in `search()` is a 3-line change: `RK = buildRanker(E)` in `load()`, then `RK.rank(S.q)`.

## MCP server

`tool_search` now calls `query.search(recs, query, filters)` and returns scores rounded to 3 decimals. The query description mentions the gps/gnss and drone/uav synonyms. Smoke test: I piped `samples/llm-agent-usage/demo_requests.jsonl` into the server and got 7 replies. The search, concept and neighbors calls return results. Request ids 6 (`show` of an unknown id) and 7 (unknown method) return the expected errors.

## Keeping it honest

- Change ranking constants in both `tools/query.py` and `site/app.js`, then run `--parity` and the eval.
- When adding queries, judge them from the records, not from ranker output, and keep the holdout split out of any tuning.
- Known weak spots: `magnetic navigation` puts two indoor magnetic-field SLAM/INS repos at ranks 2-3, ahead of MagNavPy and `concept:magnetic-nav` (rank 7). `ekf imu gnss` puts the generic `robot_localization` at rank 2, above most of the small GNSS/INS EKF repos. Rank 1 there is `sample:gnss-ins-ekf-outage`, which is on topic but was not in the judged list.
