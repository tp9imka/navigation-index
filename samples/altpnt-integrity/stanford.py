"""Stanford diagram: region classification, ASCII tally grid and a stdlib SVG writer."""

import math

REGIONS = ("nominal", "unavailable", "MI", "HMI", "unavail_MI")
BIN_EDGES = [0, 5, 10, 20, 30, 40, 50, 75, 100, 150, 250, 500, math.inf]
COLORS = {"nominal": "#2b8a3e", "unavailable": "#1c7ed6", "MI": "#f08c00",
          "HMI": "#e03131", "unavail_MI": "#9c36b5"}


def classify(pe, pl, al):
    """Regions of the Stanford diagram (Tossaint et al. 2006 / Navipedia).

    nominal: PE < PL < AL; unavailable: PE < PL, PL >= AL; MI: PL <= PE < AL with PL < AL;
    HMI: PE >= AL while PL < AL (system claims availability); unavail_MI: PE >= PL >= AL.
    """
    if pl >= al:
        return "unavail_MI" if pe >= pl else "unavailable"
    if pe < pl:
        return "nominal"
    return "HMI" if pe >= al else "MI"


def tally(rows):
    out = {r: 0 for r in REGIONS}
    for r in rows:
        out[r["region"]] += 1
    return out


def _bin(v):
    for i in range(len(BIN_EDGES) - 1):
        if v < BIN_EDGES[i + 1]:
            return i
    return len(BIN_EDGES) - 2


def ascii_diagram(rows, al):
    """Counts per (PE, PL) bin. Rows: PL (top = large). Columns: PE. Diagonal cells marked '\\'."""
    nb = len(BIN_EDGES) - 1
    grid = [[0] * nb for _ in range(nb)]
    for r in rows:
        grid[_bin(r["hpl"])][_bin(r["hpe"])] += 1
    labels = [f"{BIN_EDGES[i]:g}" for i in range(nb)]
    lines = []
    for pl_i in reversed(range(nb)):
        cells = []
        for pe_i in range(nb):
            c = grid[pl_i][pe_i]
            if c:
                cells.append(f"{c:>5}")
            else:
                cells.append("    \\" if pe_i == pl_i else "    .")
        mark = " <AL" if BIN_EDGES[pl_i] < al <= BIN_EDGES[pl_i + 1] else ""
        lines.append(f"PL>={labels[pl_i]:>4} |" + "".join(cells) + mark)
    lines.append("         +" + "-----" * nb)
    lines.append("   PE>=   " + "".join(f"{lab:>5}" for lab in labels) + "  [m]")
    t = tally(rows)
    lines.append("   " + "  ".join(f"{k}={t[k]}" for k in REGIONS))
    return "\n".join(lines)


def write_svg(path, rows, al, title="", size=520):
    """Log-log scatter of PE (x) vs PL (y) with the diagonal and alert-limit lines."""
    lo, hi = 0.5, 1000.0
    pad = 60
    span = size - 2 * pad

    def sx(v):
        return pad + span * (math.log10(min(max(v, lo), hi)) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))

    def sy(v):
        return size - pad - span * (math.log10(min(max(v, lo), hi)) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size + 160}" height="{size}" '
           f'font-family="sans-serif" font-size="11">',
           f'<rect width="100%" height="100%" fill="white"/>',
           f'<text x="{pad}" y="20" font-size="13">Stanford diagram {title}</text>',
           f'<rect x="{pad}" y="{pad}" width="{span}" height="{span}" fill="none" stroke="#333"/>']
    for d in (1, 10, 100, 1000):
        out.append(f'<text x="{sx(d):.1f}" y="{size - pad + 15}" text-anchor="middle">{d}</text>')
        out.append(f'<text x="{pad - 6}" y="{sy(d) + 4:.1f}" text-anchor="end">{d}</text>')
    out.append(f'<line x1="{sx(lo):.1f}" y1="{sy(lo):.1f}" x2="{sx(hi):.1f}" y2="{sy(hi):.1f}" stroke="#666" stroke-dasharray="4 3"/>')
    out.append(f'<line x1="{sx(al):.1f}" y1="{pad}" x2="{sx(al):.1f}" y2="{size - pad}" stroke="#e03131"/>')
    out.append(f'<line x1="{pad}" y1="{sy(al):.1f}" x2="{size - pad}" y2="{sy(al):.1f}" stroke="#e03131"/>')
    out.append(f'<text x="{size / 2}" y="{size - 20}" text-anchor="middle">horizontal position error [m]</text>')
    out.append(f'<text x="15" y="{size / 2}" transform="rotate(-90 15 {size / 2})" text-anchor="middle">'
               f'horizontal protection level [m]</text>')
    for r in rows:
        out.append(f'<circle cx="{sx(r["hpe"]):.1f}" cy="{sy(r["hpl"]):.1f}" r="2" '
                   f'fill="{COLORS[r["region"]]}" fill-opacity="0.6"/>')
    t = tally(rows)
    for i, k in enumerate(REGIONS):
        y = pad + 16 * i
        out.append(f'<circle cx="{size - pad + 20}" cy="{y}" r="4" fill="{COLORS[k]}"/>')
        out.append(f'<text x="{size - pad + 30}" y="{y + 4}">{k}: {t[k]}</text>')
    out.append(f'<text x="{size - pad + 20}" y="{pad + 16 * len(REGIONS) + 10}">AL = {al:g} m</text>')
    out.append("</svg>")
    with open(path, "w") as fh:
        fh.write("\n".join(out))
