# Submission checklist

Run H+42 to H+48, before the final push. One person reads, another checks.

## Repo and reproducibility

- [ ] Fresh clone on a second machine: `make test && make eval && make demo` pass with the README steps only.
- [ ] Python and dependency versions stated; optional deps pinned in `pyproject.toml` extras.
- [ ] Docker images pinned to tags (no `latest`); placeholder services removed or marked as such.
- [ ] Datasets: name, version, URL, licence, and fetch command in README. Large files not in git.
- [ ] Seeds fixed; results table pasted from `runs/results.md`, matching the current commit.
- [ ] README "What we did not verify" and "Known failure modes" filled in.
- [ ] Demo video linked; commit hash noted in the video or its description.

## Licence

- [ ] `LICENSE` file present (team agreed on it; Apache-2.0 / MIT / BSD are common for hackathon code).
- [ ] Event rules on IP and licence checked (some events require a specific licence or grant rights to the organiser).
- [ ] Third-party code: each copied file or vendored repo keeps its licence header; GPL-licensed code noted if you link it.
- [ ] Dataset and map licences allow your use and redistribution of any derived files you commit.

## Export control and scope

Read [export-control-and-ethics.md](../docs/export-control-and-ethics.md), then tick its
[checklist](../docs/export-control-and-ethics.md#7-checklist):

- [ ] Everything in the repo is your own work or public, with licences noted.
- [ ] No non-public technical data from any defense programme or NDA.
- [ ] No military-signal (M-code, P(Y)) processing beyond publicly documented interfaces.
- [ ] Encryption content identified; EAR 742.15(b) notification considered if applicable.
- [ ] Signal generation defaults to file output; no over-the-air transmission instructions.
- [ ] Scope is navigation, awareness or defensive detection; no targeting or payload logic.
- [ ] ML components have a documented fallback and logged decisions.
- [ ] README states test conditions and known failure modes.
- [ ] If the repo was private with international team members: you read the "what changes the picture" section of that doc.

## Secrets and hygiene

- [ ] No tokens, keys, passwords, TAK certificates (`*.p12`, `*.pem`) in the tree or history:
      `git log -p | grep -nE '(api[_-]?key|token|secret|password|BEGIN .*PRIVATE KEY)'` returns nothing real.
- [ ] `.env.example` committed, `.env` ignored.
- [ ] No personal data in logs or recordings (faces, phone numbers, precise home locations of team members).
- [ ] No venue Wi-Fi credentials or internal URLs in notes.

## Submission form

- [ ] Title and one-line summary match README.
- [ ] Team members and roles listed.
- [ ] Deck exported to PDF; video plays offline.
- [ ] Submitted before the deadline minus 30 minutes; confirmation saved.
