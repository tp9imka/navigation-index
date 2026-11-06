"""List-of-lists matrix helpers, enough for an 8-state EKF."""

import math


def zeros(n, m):
    return [[0.0] * m for _ in range(n)]


def eye(n):
    a = zeros(n, n)
    for i in range(n):
        a[i][i] = 1.0
    return a


def mul(a, b):
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def T(a):
    return [list(r) for r in zip(*a)]


def add(a, b):
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def sub(a, b):
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def mv(a, v):
    return [sum(x * y for x, y in zip(row, v)) for row in a]


def inv2(a):
    det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    return [[a[1][1] / det, -a[0][1] / det], [-a[1][0] / det, a[0][0] / det]]


def sym(a):
    n = len(a)
    return [[0.5 * (a[i][j] + a[j][i]) for j in range(n)] for i in range(n)]


def lmax2(a):
    """Largest eigenvalue of a symmetric 2x2 matrix."""
    tr = a[0][0] + a[1][1]
    det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    disc = max(tr * tr / 4.0 - det, 0.0)
    return tr / 2.0 + math.sqrt(disc)
