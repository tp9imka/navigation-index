# White Rabbit PTP Core software (wrpc-sw)

`repo:gitlab.com/ohwr/project/wrpc-sw` - <https://gitlab.com/ohwr/project/wrpc-sw>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| ? | C | ? | ? | ? | production | low |

Software for the White Rabbit PTP Core (WRPC): a bare-metal PTP daemon (PPSi) and drivers for the WRPC HDL that runs on a soft CPU inside the FPGA, giving a node sub-ns sync over fibre.

**Why it matters:** The node side of White Rabbit: if a team has a WR-capable FPGA board, this is what turns it into a synchronised timing endpoint.

**Hackathon notes:** Needs WR hardware (e.g. SPEC board + WR switch) and the wr-cores gateware. Not a 48 h starting point without the kit on the table; useful as reference for how WR extends PTP with phase tracking and link calibration.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `white-rabbit`, `ptp`, `fpga`, `ppsi`, `ohwr`

**Domains:** multi

## Related

- depends_on: [White Rabbit cores (wr-cores)](../../catalog/repos/gitlab.com__ohwr__project__wr-cores.md)
- depends_on: [PPSi](../../catalog/repos/gitlab.com__ohwr__project__ppsi.md)
- integrates_with: [White Rabbit switch software](../../catalog/repos/gitlab.com__ohwr__project__wr-switch-sw.md)

## Referenced by

- [White Rabbit (OHWR project hub)](../../catalog/repos/gitlab.com__ohwr__project__white-rabbit.md) (same_org)
- [White Rabbit calibration](../../catalog/repos/gitlab.com__ohwr__project__wr-calibration.md) (same_org)

_Indexed by lane(s): timing-network_
