# alpha-beta-CROWN

`repo:verified-intelligence/alpha-beta-crown` - <https://github.com/Verified-Intelligence/alpha-beta-CROWN>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 410 | Python | NOASSERTION | 2026-10-10 | False | active-research | low |

GPU-accelerated neural-network verifier that proves bounds on a network's outputs over a set of inputs. Winner of the VNN-COMP verification competition several years running (per its README).

**Why it matters:** One concrete answer to 'how would you assure the learned part': prove a small learned component (for example a confidence head) stays bounded over a stated input envelope.

**Hackathon notes:** Scales to small and medium networks, not to a full ViT backbone. BSD-3-style license file (GitHub reports NOASSERTION). Mention on the assurance slide; do not try to verify a feature matcher in 48 h.

**Concepts:** [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `nn-verification`, `ml-assurance`, `formal-methods`, `pytorch`

**Domains:** multi

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-09._
