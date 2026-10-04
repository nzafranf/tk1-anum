# Extracted verbatim from soal2/report/analyze.py
import numpy as np

def gaussian_pivot(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Solve a square linear system by partial-pivot Gaussian elimination."""
    u = a.astype(float).copy()
    y = b.astype(float).copy()
    n = len(y)
    for k in range(n):
        pivot = k + int(np.argmax(np.abs(u[k:, k])))
        if u[pivot, k] == 0:
            raise ValueError("Singular system")
        if pivot != k:
            u[[k, pivot]] = u[[pivot, k]]
            y[[k, pivot]] = y[[pivot, k]]
        for i in range(k + 1, n):
            factor = u[i, k] / u[k, k]
            u[i, k:] -= factor * u[k, k:]
            y[i] -= factor * y[k]
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (y[i] - np.dot(u[i, i + 1 :], x[i + 1 :])) / u[i, i]
    return x

def givens_least_squares(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Apply each Givens rotation to two rows of [A | b], then back-solve."""
    r = a.astype(float).copy()
    d = b.astype(float).copy()
    m, n = r.shape
    for i in range(n):
        for j in range(i + 1, m):
            if r[j, i] == 0:
                continue
            alpha = np.hypot(r[i, i], r[j, i])
            c, s = r[i, i] / alpha, r[j, i] / alpha
            row_i = r[i, i:].copy()
            row_j = r[j, i:].copy()
            r[i, i:] = c * row_i + s * row_j
            r[j, i:] = -s * row_i + c * row_j
            di, dj = d[i], d[j]
            d[i], d[j] = c * di + s * dj, -s * di + c * dj
            r[j, i] = 0.0
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (d[i] - np.dot(r[i, i + 1 :n], x[i + 1 :])) / r[i, i]
    return x
