# Galileo OSNMA (SIS ICD + Receiver Guidelines) - standard digest
<!-- about: res:galileo-osnma-sis-icd, res:galileo-osnma-receiver-guidelines, repo:algafix/osnma -->
**Galileo OSNMA Signal-In-Space ICD, Issue 1.1 (Oct 2023)** and **Galileo OSNMA Receiver Guidelines, Issue 1.3 (Jan 2024)** - EU / EUSPA, European GNSS Service Centre (GSC). [SIS ICD](https://www.gsc-europa.eu/sites/default/files/sites/all/files/Galileo_OSNMA_SIS_ICD_v1.1.pdf) | [Receiver Guidelines](https://www.gsc-europa.eu/sites/default/files/sites/all/files/Galileo_OSNMA_Receiver_Guidelines_v1.3.pdf) | [code: OSNMAlib](https://github.com/Algafix/OSNMA) | Read: full text of both PDFs (ICD 55 pp, RG 65 pp). Annex E (IPR) and the RG test-vector annex were skimmed, not read line by line. The IDD ICD (key/Merkle-root distribution) was not read.

Section references below are "ICD x.y" and "RG x.y".

## Problem
Civil GNSS navigation data can be forged, for example with false ephemeris or clock data from a simulator spoofer. OSNMA lets a receiver cryptographically verify that the Galileo E1-B I/NAV navigation data came from Galileo and was not modified (RG 1.2). It authenticates the **data**, not the ranging signal: "as this PVT is computed using non-verified ranging information, it cannot be considered authenticated" (RG Annex D).

## Method (protocol in brief)
- **TESLA one-way key chain.** Tags (truncated MACs) over the navigation data are broadcast first. The chain key that produced them is disclosed later, and keys go out in reverse order of generation (ICD 1.4, 5.5.2). One chain is shared by all satellites, which enables cross-authentication: OSNMA-transmitting satellites also carry tags for satellites that do not transmit OSNMA (ICD 5.2).
- **Trust anchors:**
  - An ECDSA signature authenticates the chain root key KROOT, sent in the DSM-KROOT (ICD 3.2.3, 6.3).
  - The ECDSA public key comes from the DSM-PKR, verified against a 16-leaf SHA-256 Merkle tree (ICD 3.2.2, 6.2).
  - The Merkle root is loaded at the factory or fetched from the GSC OSNMA server (RG 3.1).
- **Chain step** (ICD 6.4, Eq. 17): K_I = trunc(l_K, hash(K_{I+1} || GST_SF,I || alpha)). To verify a key, hash it back to KROOT or to a previously verified key. The number of steps follows from GST (Eq. 19).
- **Data carried (ICD Table 14):**
  - ADKD 0: ephemeris, clock and status, I/NAV word types 1-5;
  - ADKD 4: GST-UTC and GST-GPS timing parameters, word types 6 and 10;
  - ADKD 12: "slow MAC", the ADKD 0 data with the key released 10 sub-frames (5 min) later.
- **Receiver workflow (RG 4.1):**
  - cold start: Merkle root => public key => KROOT;
  - warm start: stored public key;
  - hot start: stored public key plus a verified chain key;
  - then verify the MACK structure (MACLT/MACSEQ), the chain key and the tag, and accumulate tags until the minimum equivalent tag length is reached (RG 5.5).
- **Status flags (ICD 3.1):**
  - NMAS: Test / Operational / Don't Use;
  - CPKS: Nominal, EOC, CREV, NPK, PKREV, NMT, Alert Message.
  - Renewal and revocation procedures are in ICD 5.4-5.7 and RG 4.2.

## Data and sensors
- **Signal:** Galileo E1-B I/NAV, nominal odd pages. Each page carries a 40-bit OSNMA field: 8 bits HKROOT plus 32 bits MACK (ICD 2).
- **Receiver needs:**
  - raw I/NAV page bits with CRC status, e.g. u-blox UBX-RXM-SFRBX or Septentrio GALRawINAV;
  - a time source meeting the sync requirement;
  - the Merkle root, plus optionally the public key, from GSC.
- **Hardware:** no antenna or RF changes needed.
- **Public test data:** the RG references test vectors for two configurations and for every renewal/revocation step, downloadable from the GSC portal (RG 1.1, Annex B). OSNMAlib also ships recorded corner cases.
- TEXBAT predates OSNMA (GPS L1 only), so it cannot exercise OSNMA. See the [TEXBAT card](../dataset-cards/texbat.md) for signal-level spoofing.

## Key protocol parameters (as stated)
- **Bandwidth:** 15 OSNMA messages per 30 s sub-frame, so 120 bits HKROOT plus 480 bits MACK every 30 s (ICD 2).
- **Tag length** l_t: 20, 24, 28, 32 or 40 bits (ICD Table 11). **Key length** l_K: 96-256 bits in 8-bit steps (ICD Table 10). **MACSEQ:** 12 bits (ICD 4.1.2).
- **MAC / hash functions:** HMAC-SHA-256 or CMAC-AES (ICD Table 9). Chain hash is SHA-256 or SHA3-256 (ICD 3.2.3.4).
- **Signatures:** ECDSA P-256/SHA-256 with a 512-bit signature, or P-521/SHA-512 with a 1056-bit signature (ICD Table 15).
- **Tags per MACK** = floor((480 - l_K) / (l_t + 16)) (ICD Eq. 8). The RG test configurations use 40-bit tags, 128-bit keys, 6 tags per MACK, ECDSA P-256 and NBDK 8 (RG Annex B, Tables 11-12).
- **Key disclosure delay:** tags are verified with the key in the **next** MACK, i.e. 30 s later. ADKD 12 tags wait 10 more sub-frames (ICD 5.8.2).
- **Time sync requirement:** T_L = 30 s. A receiver with GST uncertainty better than that can use all tags. With accuracy better than T_L + 300 s, only slow MAC (ADKD 12) may be used. Otherwise "the OSNMA protocol shall not be used" (RG 2.1).
  - Checked as |GST_SIS - GST_Rx| < T_L/2 (RG 5.3.1, Eq. 1), equivalently B < T_L/2 (RG Annex C, Eq. 6).
  - Annex C warns: "the timing solution computed with the authenticated data is not itself authenticated". Re-syncing the clock from it carries risk.
- **DSM sizes:**
  - DSM-KROOT is 7-14 blocks of 104 bits (ICD Table 7); DSM-PKR is 13-16 blocks (ICD Table 3).
  - Blocks are spread across satellites, and a receiver can combine blocks from several satellites (ICD 5.3).
  - The RG says to discard an incomplete DSM-KROOT after 1 h and an incomplete DSM-PKR after 13 h (RG 3.2, 3.3).
- **Material refresh:**
  - The public key is broadcast in DSM-PKR every 6 h (00, 06, 12, 18 GST) for 30 min (ICD 5.4).
  - A new floating KROOT comes at least once per day and at most once per hour (ICD 5.5.1).
  - The receiver must re-verify the NMA status via the KROOT signature at least once per hour (RG 4.2.1).
- **Coverage:** OSNMA is sent by a subset of satellites, "20 at the time of publishing" (ICD 1.4). The subset changes and cannot be predicted (ICD 5.2).
- **Minimum equivalent tag length** L_t^min: **not stated**. It is deferred to "the future Galileo Authentication Service Definition Document" and should be configurable (RG 5.5.6). Tag accumulation rules are in ICD 5.8.1 and RG 5.5.6.
- **Time to first authenticated fix (TTFAF): not stated in either document.** The documents only bound the parts: a key arrives 30 s after its tags, the KROOT must be assembled, and L_t^min is unspecified. The OSNMAlib README (not the standard, not verified by us) claims "TTFAF as low as 44 seconds in hot start" with its recovery optimizations, citing their IEEE TAES 2025 paper.

## Limitations
- Stated in the documents:
  - Navigation data only; the ranging measurements and therefore the PVT are not authenticated (RG Annex D).
  - Security depends entirely on the receiver's time-sync guarantee (RG 2.1, Annex C).
  - Receiver integrity protection of the stored keys and root is the receiver's responsibility (RG 2.3).
  - The RG Annex D suggests complementary checks: vestigial-signal search, correlation monitoring, AGC versus C/N0, RAIM, PVT dynamics, clock cross-check, IMU/odometer, multi-antenna DoA. It also notes that OSNMA's unpredictable tag and key bits make replay harder.
- Our read:
  - OSNMA does not stop a meaconer (record and replay with delay) whose delay stays inside the time-sync budget. The defence against that is the clock-consistency and power checks above.
  - TTFAF (tens of seconds even in hot start, per OSNMAlib) means a cold-starting receiver flies or drives unauthenticated for a while.
  - Galileo E1 only, so GPS/GLONASS/BeiDou data are not authenticated in this ICD (PRND 37-254 reserved, ICD Table 12).
  - Public key ID changed from 1 to 2 on 2025-12-10 (OSNMAlib README). Old recordings need the old key.

## Code, weights, license
- [Algafix/OSNMA](https://github.com/Algafix/OSNMA) (OSNMAlib):
  - EUPL-1.2 (GitHub API); last push 2026-10-14; not archived.
  - Python 3.10-3.12.
  - Inputs: Septentrio SBF, u-blox UBX (file or live), galmon live, GNSS-SDR UDP, Android GnssLogger.
  - Passes the ICD test vectors (CI badges). Ships the current Merkle root and public keys.
  - See the [integration card](../integration-cards/algafix__osnma.md).
- Alternatives listed in the index:
  - [daniestevez/galileo-osnma](https://github.com/daniestevez/galileo-osnma): Rust, Apache-2.0 per GitHub API, last push 2026-03-04;
  - [nlsfi/fgi-osnma](https://github.com/nlsfi/fgi-osnma): GPL-3.0, last push 2023-11-16, likely stale for ICD 1.1 changes (not checked).
- **Document terms:** the ICD and RG are EU copyright. Reproduction must carry the Terms of Use unmodified, and alteration or translation needs written permission. Implementing the protocol is authorised under ICD Annex E (IPR authorisation). Summarising parameters, as done here, is fine. Do not paste the documents into the repo.

## Reproduction effort (estimate)
Estimate:
- **Fastest path:** clone OSNMAlib and run `custom_run/run.py` on the bundled SBF recording. Expect about 15 min on a laptop (per the integration card); no GPU needed.
- **Live:** a u-blox receiver with Galileo E1 and RXM-SFRBX enabled (F9P or M10 class), plus NTP or a disciplined clock to meet T_L. Expect 1-2 h including receiver configuration.
- **Not reproducible here:** formal security claims (L_t^min not yet published), and IDD server authentication of the cryptographic material (not implemented in OSNMAlib per its README "Future development").

## What a hackathon team can take from it
- **An "authenticated ephemeris" trust signal:** feed only satellites whose ADKD0/ADKD12 data verified into the PVT, or into the GNSS update of your EKF, and show the per-satellite status live. OSNMAlib's JSON status log is the plug point. Wire u-blox through [pyubx2](../integration-cards/semuconsulting__pyubx2.md), or use an SDR through [GNSS-SDR](../integration-cards/gnss-sdr__gnss-sdr.md).
- **Respect the time-sync rule:** check |GST_SIS - GST_Rx| < 15 s against an independent clock (RTC or NTP) before trusting tags. Do not re-sync the clock from the same GNSS solution you are authenticating (RG Annex C).
- **Pair OSNMA with signal-level checks.** It covers the data-forgery attacks (simulator, falsified ephemeris) that [Kriezis 2025](kreizis-ion-itm-2025-spoofing.md) found ephemeris checks cannot catch when the spoofer relays live data. Combine it with C/N0, AGC and clock-drift checks for replay ([Psiaki and Humphreys 2016](psiaki-humphreys-2016-gnss-spoofing-detection.md) rows D7/D9).
- **Demo metrics:** TTFAF and the percentage of authenticated satellites over time, in cold, warm and hot start. "Authentication dropped while C/N0 stayed high" is a strong spoofing cue for an alarm that hands over to INS/VIO.
