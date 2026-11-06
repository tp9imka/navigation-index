# Sample: Drone Remote ID decoder, track table and TAK output

`sample:remote-id-to-tak` - code and walkthrough in [samples/remote-id-to-tak](../../samples/remote-id-to-tak/)

Passive airspace awareness from broadcast Remote ID (ASTM F3411 / ASD-STAN EN 4709-002). A stdlib decoder for Open Drone ID messages and packs, validated field-for-field against opendroneid-core-c, extracts payloads from Wi-Fi beacon, Wi-Fi NAN and BLE captures, feeds a per-UAS track table with spoofing plausibility flags, and emits a UAS track plus operator point as Cursor-on-Target via PyTAK.

**Verification:** Ran on 2026-11-06 (macOS arm64, Python 3.14.7 and 3.12.14, Apple clang 21). odid.py matched opendroneid-core-c master 849c03a field-for-field (exact float32/double values, raw string bytes) on 500 core-c-encoded messages/packs, 500 random raw messages, 81 unique payloads from the three public opendroneid/wireshark-dissector captures, plus a live 600-vector batch; 5 planted decoder mutations each failed the suite. capture.py decoded 42 NAN+beacon packs, 21 beacon packs with positions and 244 CRC-OK BT5 long-range packs from those captures. rid_to_cot.py sent 256 CoT events through PyTAK 7.6.1 to a local TCP sink (synthetic scenario) and 10 to a UDP sink (real beacon capture). Not verified: any live radio reception, a real TAK server or ATAK rendering, the core-c cmake build or its own odidtest (cmake absent; library compiled directly with cc), Auth message semantics beyond decoding, anomaly thresholds against real spoofing.

**Concepts:** [Counter-UAS and drone detection](../../catalog/concepts/counter-uas.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `remote-id`, `astm-f3411`, `opendroneid`, `cot`, `tak`, `pytak`, `spoofing-detection`, `ble`, `wifi-nan`

## Related

- evaluated_on: [Open Drone ID Core C](../../catalog/repos/opendroneid__opendroneid-core-c.md)
- uses: [Open Drone ID Wireshark dissector](../../catalog/repos/opendroneid__wireshark-dissector.md)
- uses: [PyTAK](../../catalog/repos/snstac__pytak.md)
- integrates_with: [OpenDroneID Android receiver](../../catalog/repos/opendroneid__receiver-android.md)
- integrates_with: [RID (ESP32 Remote ID receiver)](../../catalog/repos/peterjburke__rid.md)
- integrates_with: [drone-mesh-mapper](../../catalog/repos/colonelpanichacks__drone-mesh-mapper.md)
- alternative_to: [DragonSync](../../catalog/repos/alphafox02__dragonsync.md)
- integrates_with: [uav_electronic_ids](../../catalog/repos/sxjack__uav_electronic_ids.md)
- uses: [FAA - Remote Identification of Drones](../../catalog/resources/faa-remote-id.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)

_Indexed by lane(s): samples_
