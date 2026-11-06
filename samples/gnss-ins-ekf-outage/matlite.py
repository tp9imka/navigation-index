"""Tiny dense-matrix helpers (lists of lists). Enough for an 8-state EKF."""


def zeros(n, m):
    return [[0.0] * m for _ in range(n)]


def eye(n, scale=1.0):
    out = zeros(n, n)
    for i in range(n):
        out[i][i] = scale
    return out


def diag(values):
    out = zeros(len(values), len(values))
    for i, v in enumerate(values):
        out[i][i] = v
    return out


def transpose(a):
    return [list(row) for row in zip(*a)]


def matmul(a, b):
    bt = transpose(b)
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in a]


def add(a, b):
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def sub(a, b):
    return [[x - y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def scale(a, k):
    return [[x * k for x in row] for row in a]


def inv2(a):
    (p, q), (r, s) = a
    det = p * s - q * r
    return [[s / det, -q / det], [-r / det, p / det]]


def symmetrize(a):
    n = len(a)
    return [[0.5 * (a[i][j] + a[j][i]) for j in range(n)] for i in range(n)]
