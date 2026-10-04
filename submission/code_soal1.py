# Extracted verbatim from soal1/soal1.ipynb
import numpy as np

def lu_dense(B: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    LU = B.astype(float).copy()
    N = LU.shape[0]
    perm = np.arange(N)
    for k in range(N - 1):
        # pivot: elemen dengan nilai mutlak terbesar di kolom k, baris k..N-1
        r = k + int(np.argmax(np.abs(LU[k:, k])))
        if LU[r, k] == 0.0:
            raise ValueError(f'B singular: kolom {k} tidak punya pivot tak-nol')
        if r != k:
            LU[[k, r], :] = LU[[r, k], :] # tukar seluruh baris, termasuk multiplier lama
            perm[[k, r]] = perm[[r, k]]
        # multiplier l_ik disimpan di tempat elemen yang dieliminasi
        LU[k + 1:, k] /= LU[k, k]
        # baris i dikurangi l_ik * baris k (kolom k+1 ke kanan)
        LU[k + 1:, k + 1:] -= np.outer(LU[k + 1:, k], LU[k, k + 1:])
    if LU[N - 1, N - 1] == 0.0:
        raise ValueError('B singular: pivot terakhir nol')
    return LU, perm

def lu_band(AB: np.ndarray, p: int, q: int) -> tuple[np.ndarray, np.ndarray]:
    AB = AB.copy()
    d = p + q
    N = AB.shape[1]
    piv = np.zeros(N, dtype=int)
    for k in range(N):
        i_maks = min(N - 1, k + p) 
        j_maks = min(N - 1, k + p + q) 
        r = k + int(np.argmax(np.abs(AB[d:d + i_maks - k + 1, k])))
        if AB[d + r - k, k] == 0.0:
            raise ValueError(f'B singular: kolom {k} tidak punya pivot tak-nol')
        piv[k] = r
        js = np.arange(k, j_maks + 1)
        if r != k:
            sementara = AB[d + k - js, js]
            AB[d + k - js, js] = AB[d + r - js, js]
            AB[d + r - js, js] = sementara
        js = js[1:]
        for i in range(k + 1, i_maks + 1):
            AB[d + i - k, k] /= AB[d, k]
            AB[d + i - js, js] -= AB[d + i - k, k] * AB[d + k - js, js]
    return AB, piv
