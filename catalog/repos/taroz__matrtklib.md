# MatRTKLIB

`repo:taroz/matrtklib` - <https://github.com/taroz/MatRTKLIB>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 100 | MATLAB | MIT | 2025-03-08 | False | active-research | medium |

MATLAB wrapper exposing RTKLIB functions and data structures (observations, navigation data, solutions) as MATLAB objects.

**Why it matters:** Lets MATLAB users script RTKLIB processing and analysis without writing C.

**Hackathon notes:** Requires MATLAB. Useful if the team already lives in MATLAB for analysis plots. Since January 2025 the backend is MALIB (the RTKLIB successor), not RTKLIB 2.4.3; pre-compiled mex files ship for Windows, Ubuntu and macOS.

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [RTK / PPP precise positioning](../../catalog/concepts/gnss-rtk-ppp.md)

**Tags:** `matlab`, `rtklib-wrapper`

**Domains:** multi

## Related

- depends_on: [RTKLIB](../../catalog/repos/tomojitakasu__rtklib.md)
- same_org: [GSDC 2023 solution (taroz)](../../catalog/repos/taroz__gsdc2023.md)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
