# Export control and ethics

> **Not legal advice.** This page is practical orientation for a hackathon team working on
> open-source navigation code. It is not legal advice, it is not complete, and rules change.
> If your project involves controlled hardware, non-public technical data, a defense
> customer, foreign team members on non-public work, or any RF transmission, ask your
> organisation's export-control or legal office, or the relevant authority, before you act.
> Where this page cites regulation text, read the primary source yourself.

The hub's scope is navigation, localization, PNT resilience, autonomy, situational
awareness, defensive EW and counter-UAS detection. Weapon terminal guidance, targeting and
offensive payloads are out of scope ([AGENTS.md](../AGENTS.md)).

Contents:

1. [Export control basics for open-source navigation code](#1-export-control-basics-for-open-source-navigation-code)
2. [What changes the picture](#2-what-changes-the-picture)
3. [GNSS signal simulation and RF transmission](#3-gnss-signal-simulation-and-rf-transmission)
4. [Drone flight rules](#4-drone-flight-rules)
5. [Responsible AI principles](#5-responsible-ai-principles)
6. [Dual-use etiquette for a public repo](#6-dual-use-etiquette-for-a-public-repo)
7. [Checklist](#7-checklist)

## 1. Export control basics for open-source navigation code

The US has two main regimes. Other countries have their own, and the EU has one regulation
for dual-use items.

| Regime | Administered by | Covers | Primary source |
|--------|-----------------|--------|----------------|
| **EAR** (Export Administration Regulations, 15 CFR 730-774) | Commerce, Bureau of Industry and Security ([BIS](https://www.bis.gov/)) | Commercial and dual-use items, software and technology | [eCFR Title 15](https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C) |
| **ITAR** (International Traffic in Arms Regulations, 22 CFR 120-130) | State, Directorate of Defense Trade Controls ([DDTC](https://www.pmddtc.state.gov/)) | Defense articles, technical data and defense services on the US Munitions List | [eCFR Title 22](https://www.ecfr.gov/current/title-22/chapter-I/subchapter-M) |
| **EU dual-use regulation** (EU) 2021/821 | National authorities of each member state | Dual-use items, software, technology; Category 7 is navigation and avionics | [Index entry](../catalog/resources/eu-dual-use-regulation-2021-821.md) |

### Published information is outside the EAR

Under 15 CFR 734.3(b)(3), information and software that is **published** as described in
734.7 is not subject to the EAR
([15 CFR 734.3](https://www.law.cornell.edu/cfr/text/15/734.3)). Section 734.7 says
unclassified technology or software is published when it has been made available to the
public without restrictions on further dissemination, and lists ways that happens,
including "posting on the Internet on sites available to the public"
([15 CFR 734.7](https://www.law.cornell.edu/cfr/text/15/734.7); index entry:
[734.7](../catalog/resources/ecfr-ear-734-7-published.md)).

Practical reading, consistent with the Linux Foundation's guide
([The EAR and Open Source Software](../catalog/resources/linux-foundation-ear-open-source.md)):

- Code you write and push to a **public** GitHub repo, with no restriction on who may read
  it, is generally published and outside the EAR.
- **Encryption is the exception to know.** Encryption source classified under 5D002 stays
  subject to the EAR unless it meets 742.15(b), which involves a notification step
  ([15 CFR 734.7(b)](https://www.law.cornell.edu/cfr/text/15/734.7);
  [EFF explainer](../catalog/resources/eff-export-encryption-source-explained.md)). This can
  matter if your PNT code adds signal or message authentication. Verifying Galileo OSNMA
  signatures is a different case from shipping your own encryption, but check rather than
  assume.
- **Private repos are not published.** Sharing a private repo with a foreign national can
  count as an export (a "deemed export" when it happens inside the US)
  ([Linux Foundation guide](../catalog/resources/linux-foundation-ear-open-source.md)).

### EAR99

Items subject to the EAR that are not listed on the Commerce Control List are designated
EAR99 ([15 CFR 734.3(c)](https://www.law.cornell.edu/cfr/text/15/734.3)). Most commercial
software and hardware is EAR99. EAR99 is not "uncontrolled": end-use and end-user
prohibitions in Part 744 apply to items subject to the EAR, and 744.21 covers certain
Russia and Belarus military end uses "for all items subject to the EAR"
([15 CFR 744.1](https://www.law.cornell.edu/cfr/text/15/744.1)). Published code avoids the
EAR; a physical box you ship does not.

### ITAR public domain is narrower

ITAR defines public domain as information "published and generally accessible or
available to the public" through listed routes - bookstores, subscriptions, libraries,
patents, open conferences, fundamental research at accredited US universities - and,
for general public release in any other form, only "after approval by the cognizant U.S.
Government department or agency"
([22 CFR 120.34](https://www.law.cornell.edu/cfr/text/22/120.34)). Practical consequence,
as university compliance offices put it: an individual cannot simply put ITAR-controlled
technical data into the public domain by posting it
([Stony Brook guide](../catalog/resources/stonybrook-export-publicly-available.md)).

For a hackathon this means: **build only from public civil signals and published methods.**
If anyone on the team has seen non-public data from a defense programme, keep it out of
the repo entirely.

## 2. What changes the picture

The same navigation algorithm can sit in very different control situations. Things that
should make you stop and ask:

| Change | Why it matters |
|--------|----------------|
| **Military GNSS** (M-code, P(Y) beyond the public interface level) or **anti-jam / adaptive antenna** technology | GNSS receiving equipment is controlled under ECCN 7A005 and related entries; a 2018 BIS rule placed adaptive-antenna GNSS receivers under 7A005.b while items otherwise described in 7A005.a remain ITAR ([Federal Register, 20 Dec 2018](https://www.govinfo.gov/content/pkg/FR-2018-12-20/html/2018-27542.htm)). The [Stony Brook guide](../catalog/resources/stonybrook-export-publicly-available.md) notes military GNSS items may be ITAR or EAR controlled. |
| **Inertial navigation hardware and navigation equipment** | CCL Category 7 covers navigation and avionics, with 7A994 catching other navigation equipment and aircraft INS not controlled elsewhere. Classification depends on performance parameters; check the current CCL, not a summary. |
| **A specific defense end use or customer** | Designing or modifying something for a defense article, or helping foreign persons do so, can become a **defense service**: "the furnishing of assistance (including training) to foreign persons... in the design, development... of defense articles" ([22 CFR 120.32](https://www.law.cornell.edu/cfr/text/22/120.32)). Integrating your code into a particular military platform is different from publishing a general algorithm. |
| **Non-public technical data** from a sponsor, NDA, or classified context | Not published, so the exclusions above do not apply. |
| **Shipping hardware** (a built prototype, an SDR loaded with your firmware) across borders | Physical items are classified on their own; EAR99 end-use rules still apply. |
| **Restricted parties or sanctioned destinations** | End-user and destination controls apply regardless of classification. |
| **EU / UK teams** | The EU regulation has its own public-domain and basic-research notes ([2021/821](../catalog/resources/eu-dual-use-regulation-2021-821.md)); the Commission's research guidance has a red-flag checklist and says to contact the national authority when control status is unclear ([Recommendation 2021/1700](../catalog/resources/eu-recommendation-2021-1700-research.md)). |
| **Weapon autonomy** | DoD Directive 3000.09 governs autonomy in weapon systems; navigation and awareness tools sit outside it, weapon autonomy does not ([DoDD 3000.09](../catalog/resources/dodd-3000-09-autonomy-weapons-2023.md)). This hub stays on the navigation side. |

## 3. GNSS signal simulation and RF transmission

**Do not transmit GNSS signals, jamming or spoofing over the air.** Generate signals to
files, process them in software, or use cables and shielded enclosures where you are
authorised to do so.

Why:

- **United States.** "No person shall willfully or maliciously interfere with or cause
  interference to any radio communications of any station licensed or authorized by or
  under this chapter or operated by the United States Government"
  ([47 U.S.C. 333](https://www.law.cornell.edu/uscode/text/47/333)). FCC enforcement material
  states that, unless you are an authorised federal user, operating a jammer is illegal
  even on private property, and that marketing, selling or importing even a single jammer
  or GPS blocker is illegal ([FCC jammer enforcement](https://www.fcc.gov/general/jammer-enforcement)).
- **United Kingdom.** Ofcom states it is illegal, unless authorised, to use apparatus for the
  purpose of interfering with wireless telegraphy (Wireless Telegraphy Act 2006, s.68)
  ([Ofcom: rules on using radio equipment](https://www.ofcom.org.uk/spectrum/radio-equipment/radio-spectrum-and-the-law)).
  A 2026 government call for evidence notes possession is not currently prohibited as such,
  while use and supply of non-compliant equipment are covered
  ([GOV.UK call for evidence](https://www.gov.uk/government/calls-for-evidence/possession-of-radiofrequency-jammers-and-the-relevant-legal-framework/possession-of-radiofrequency-jammers-and-the-relevant-legal-framework)).
- **Elsewhere.** Most jurisdictions treat unlicensed transmission in GNSS bands the same way.
  Check your national regulator.
- **Safety.** GNSS interference affects aircraft and ships well beyond your test area
  ([EASA SIB 2022-02R4](../catalog/resources/easa-sib-2022-02r4.md),
  [FAA SAFO 24002](../catalog/resources/faa-safo-24002.md)). A spoofed signal does not stay
  in your lab.

How to work instead:

- **File-based simulation.** [GPS-SDR-SIM](../catalog/repos/osqzss__gps-sdr-sim.md) and
  [OSNMA-SDR-SIM](../catalog/repos/haiyang-wong__osnma-sdr-sim.md) write IQ files that
  [GNSS-SDR](../catalog/repos/gnss-sdr__gnss-sdr.md) reads directly. No radio involved.
- **Recorded data.** [TEXBAT](../catalog/resources/ut-texbat.md) spoofing recordings, phone
  logs from the [multi-frequency spoofing dataset](../catalog/repos/s7am1na__gnss-spoofing-dataset.md),
  and community datasets from [Jammertest](../catalog/resources/jammertest-norway.md), where
  Norwegian authorities transmit under controlled conditions.
- **Cabled or shielded only** for tools that can drive an SDR, such as
  [multi-sdr-gps-sim](../catalog/repos/mictronics__multi-sdr-gps-sim.md), whose catalog notes say
  the same: radiating GNSS signals over the air is illegal in most jurisdictions. "Shielded"
  means a proper RF enclosure, not a box in the corner, and still needs whatever
  authorisation your organisation requires.
- **Receive-only monitoring is fine** in general: ADS-B ([readsb](../catalog/repos/wiedehopf__readsb.md)),
  AIS ([AIS-catcher](../catalog/repos/jvde-github__ais-catcher.md)), spectrum display
  ([Gqrx](../catalog/repos/gqrx-sdr__gqrx.md)), phone GNSS logs. Some countries restrict
  decoding or sharing certain received content; check locally.
- **Software spoofing for evaluation** - injecting an offset into recorded GNSS
  measurements - gives you the test you need (primer
  [chapter 9](primer/09-evaluation-and-datasets.md)) with no RF at all.

## 4. Drone flight rules

Plan to do everything in SITL (primer [chapter 6](primer/06-autopilots-and-c2.md)). If you
must fly:

- **United States.** Part 107 sets a 400 ft above-ground limit (with a structure exception)
  ([14 CFR 107.51](https://www.law.cornell.edu/cfr/text/14/107.51)) and visual line of
  sight rules apply (14 CFR 107.31); Remote ID applies to most drones
  ([FAA Remote ID](../catalog/resources/faa-remote-id.md)).
- **EU.** In the open category under Regulation (EU) 2019/947, operations are limited to
  visual line of sight and 120 m above the surface; anything beyond needs the specific
  category with authorisation or a declaration
  ([EASA: understanding the open category](https://www.easa.europa.eu/en/the-agency/faqs/understanding-open-category)).
- **Elsewhere and always:** check the national aviation authority, airspace restrictions and
  the venue's rules. Restricted areas near military sites and airports are common at
  defense events.
- **GNSS-denied flight testing** is exactly the case where a fly-away is most likely. Keep a
  safety pilot with manual override, a geofence enforced on more than GNSS, and a tested
  failsafe. Never combine a real flight with your own interference test.
- **Remote ID and DroneID decoding** for detection is receive-only, but respect privacy: do
  not publish operator locations of real third-party drones.

## 5. Responsible AI principles

If your project uses ML (learned matching, detection, learned odometry), defense judges
increasingly ask how it maps to these principles:

- **DoD AI ethical principles:** responsible, equitable, traceable, reliable, governable
  ([DoD announcement](../catalog/resources/dod-ai-ethical-principles-2020.md)).
- **NATO principles of responsible use:** lawfulness; responsibility and accountability;
  explainability and traceability; reliability; governability; bias mitigation
  ([NATO AI strategy summary](../catalog/resources/nato-ai-strategy-principles-2021.md)).

What that means for a navigation system, concretely:

| Principle | Navigation practice |
|-----------|---------------------|
| Traceable | Log inputs, estimates, covariances and every source switch with timestamps |
| Reliable | Report uncertainty honestly; evaluate on data unlike your training set; publish failure cases |
| Governable | Provide a way to disengage a learned component and fall back to a classical estimator or a human; make it testable |
| Explainable | Show *why* a fix was rejected (innovation too large, match inliers too few) |
| Equitable / bias | State which terrain, season, lighting and sensors you trained and tested on |
| Lawful | Stay inside the scope boundaries in this page |

## 6. Dual-use etiquette for a public repo

Navigation code is dual-use by nature. Some norms that keep a public project defensible:

- **Frame it defensively and say so** in the README: resilience, integrity monitoring,
  detection, safe operation when GNSS is degraded.
- **No operational targeting, terminal guidance or payload logic.** Not in code, not in
  examples, not in issues.
- **No ready-to-radiate attack tooling.** File-based signal generation for testing receivers
  is common practice; a turnkey "spoof this aircraft" script is not. Default outputs to files.
- **Keep data provenance clean.** Only public data, with licences recorded. No imagery or
  logs from real operations, no personal data, no real third-party flight tracks without
  need.
- **Be honest about performance.** Report test conditions and failure modes; do not imply
  field validation you did not do. Vendor and press claims in this hub are marked as claims
  for the same reason.
- **Encryption and authentication code:** note in the README whether the repo includes
  cryptography and check the EAR encryption notification point above.
- **Contributors:** if anyone contributes from a defense employer, they should follow their
  employer's release process; that is their call, not the repo's.
- **Licence and notice:** add a short NOTICE that the software is provided for research and
  resilience purposes and that users are responsible for complying with export and radio
  regulations where they use it. It does not change the law; it does set expectations.

## 7. Checklist

Before you push:

- [ ] Everything in the repo is either your own work or public, with licences noted.
- [ ] No non-public technical data from any defense programme or NDA.
- [ ] No military-signal (M-code, P(Y)) processing beyond publicly documented interfaces.
- [ ] Encryption content identified; EAR 742.15(b) notification considered if applicable.
- [ ] Signal generation defaults to file output; no over-the-air transmission instructions.
- [ ] Scope is navigation, awareness or defensive detection; no targeting or payload logic.
- [ ] ML components have a documented fallback and logged decisions.
- [ ] README states test conditions and known failure modes.

Before you fly or transmit anything: stop and get explicit authorisation from the people
responsible. This page cannot give it.

## Sources

Index resources: [Linux Foundation: EAR and open source](../catalog/resources/linux-foundation-ear-open-source.md),
[15 CFR 734.7](../catalog/resources/ecfr-ear-734-7-published.md),
[EFF encryption explainer](../catalog/resources/eff-export-encryption-source-explained.md),
[Stony Brook public domain guide](../catalog/resources/stonybrook-export-publicly-available.md),
[EU 2021/821](../catalog/resources/eu-dual-use-regulation-2021-821.md),
[EU Recommendation 2021/1700](../catalog/resources/eu-recommendation-2021-1700-research.md),
[DoDD 3000.09](../catalog/resources/dodd-3000-09-autonomy-weapons-2023.md),
[DoD AI principles](../catalog/resources/dod-ai-ethical-principles-2020.md),
[NATO AI principles](../catalog/resources/nato-ai-strategy-principles-2021.md),
[FAA Remote ID](../catalog/resources/faa-remote-id.md),
[EASA SIB 2022-02R4](../catalog/resources/easa-sib-2022-02r4.md),
[FAA SAFO 24002](../catalog/resources/faa-safo-24002.md),
[Jammertest](../catalog/resources/jammertest-norway.md),
and the concept page [policy, export control and ethics](../catalog/concepts/policy-ethics.md).

Official sources checked for this page (November 2026):
[15 CFR 734.3](https://www.law.cornell.edu/cfr/text/15/734.3),
[15 CFR 734.7](https://www.law.cornell.edu/cfr/text/15/734.7),
[15 CFR 744.1](https://www.law.cornell.edu/cfr/text/15/744.1),
[22 CFR 120.32](https://www.law.cornell.edu/cfr/text/22/120.32),
[22 CFR 120.34](https://www.law.cornell.edu/cfr/text/22/120.34),
[Federal Register 2018-27542 (7A005)](https://www.govinfo.gov/content/pkg/FR-2018-12-20/html/2018-27542.htm),
[47 U.S.C. 333](https://www.law.cornell.edu/uscode/text/47/333),
[14 CFR 107.51](https://www.law.cornell.edu/cfr/text/14/107.51),
[Ofcom radio equipment rules](https://www.ofcom.org.uk/spectrum/radio-equipment/radio-spectrum-and-the-law),
[GOV.UK jammer possession call for evidence](https://www.gov.uk/government/calls-for-evidence/possession-of-radiofrequency-jammers-and-the-relevant-legal-framework/possession-of-radiofrequency-jammers-and-the-relevant-legal-framework),
[EASA open category FAQ](https://www.easa.europa.eu/en/the-agency/faqs/understanding-open-category).
The [FCC jammer enforcement page](https://www.fcc.gov/general/jammer-enforcement) and
[BIS](https://www.bis.gov/) / [DDTC](https://www.pmddtc.state.gov/) home pages are the
authorities' entry points; the FCC statements above were confirmed through FCC enforcement
advisories rather than that page, which refused automated access.
