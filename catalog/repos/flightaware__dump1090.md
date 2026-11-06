# dump1090-fa

`repo:flightaware/dump1090` - <https://github.com/flightaware/dump1090>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,152 | C | NOASSERTION | 2026-11-03 | False | production | medium |

FlightAware's maintained Mode S/ADS-B decoder (dump1090-fa), a GitHub fork and successor of dump1090-mutability, supporting RTL-SDR, bladeRF, HackRF, LimeSDR and SoapySDR devices.

**Why it matters:** Widely packaged alternative to readsb for the same ADS-B situational-awareness use.

**Hackathon notes:** apt-installable on Raspberry Pi OS from FlightAware's own package repository (it is not in Debian main), or build the .deb from source; pick either this or readsb, not both.

**Concepts:** [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md)

**Tags:** `ads-b`, `rtl-sdr`

**Domains:** air

## Related

- alternative_to: [readsb](../../catalog/repos/wiedehopf__readsb.md)

## Referenced by

- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [ADSBCOT](../../catalog/repos/snstac__adsbcot.md) (integrates_with)
- [readsb](../../catalog/repos/wiedehopf__readsb.md) (alternative_to)

_Indexed by lane(s): defense-context_

_GitHub metadata fetched 2026-11-06._
