## What changed

<!-- One or two sentences. Which records, samples, planners or pages. -->

## What it ran on

<!-- Tick one or more. Name the dataset, simulator or vehicle. "Not run" is an honest answer. -->

- [ ] synthetic
- [ ] SITL
- [ ] real
- [ ] not run (docs or records only)

## Gate commands run

<!-- Paste the commands and their output. See CONTRIBUTING.md, "The gate a PR must pass". -->

```text
$ python3 tools/build.py | tail -3
$ python3 tools/check_links.py
$ python3 tools/check_public.py
```

## Checklist

- [ ] `python3 tools/check_links.py` prints `broken: 0`
- [ ] `python3 tools/check_public.py` prints 0 hits
- [ ] `python3 tools/build.py` prints `dangling: 0 bad concepts: 0`
- [ ] Every new number says what it ran on and is in a file in the repo
- [ ] Plain hyphen `-` only (no em or en dashes), `=>` for arrows
- [ ] In scope: the vehicle's own navigation; no targeting, homing, intercept or weapons guidance
