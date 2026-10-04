"""Build the two TK 1 reports, cover, combined PDF, and submission ZIP.

Run from the project root with: python build_submission.py
Requires Python (PyMuPDF), MiKTeX pdflatex, and the existing report assets.
"""

from __future__ import annotations

import csv
import subprocess
import zipfile
from pathlib import Path

import pymupdf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "submission"
BUILD = OUT / "build"
STEM = "TK A12 2406402542 2406429020 2406437893 2306227311"

PEOPLE = [
    ("2406402542", "Naufal Zafran Fadil", "ttd_zafran.png"),
    ("2406429020", "WILLIAM JONNATAN", "ttd_william.png"),
    ("2406437893", "TSANIYA FINI ARDIYANTI", "ttd_fini.jpg"),
    ("2306227311", "Franky Raymarcell Sinaga", "ttd_franky.png"),
]


def run_latex(source: Path, output: Path) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={output}",
                source.name,
            ],
            cwd=source.parent,
            check=True,
            stdout=subprocess.DEVNULL,
        )
    return output / f"{source.stem}.pdf"


def make_cover() -> Path:
    cards = []
    for npm, name, sig in PEOPLE:
        cards.append(
            rf"\begin{{minipage}}[t]{{0.46\textwidth}}\centering"
            rf"\includegraphics[width=3.2cm,height=1.75cm,keepaspectratio]{{../ignore/{sig}}}\\[-2pt]"
            rf"\rule{{5.8cm}}{{0.35pt}}\\[3pt]"
            rf"\textbf{{{name}}}\\{npm}"
            rf"\end{{minipage}}"
        )
    tex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[indonesian]{babel}
\usepackage{lmodern,graphicx,geometry,booktabs}
\geometry{margin=2.54cm}
\begin{document}
\thispagestyle{empty}
\begin{center}
{\large UNIVERSITAS INDONESIA\\[8pt] ANALISIS NUMERIK -- SEMESTER GASAL 2026/2027}\par
\vspace{1.3cm}
{\LARGE\bfseries TK 1: Sistem Persamaan Linear dan Least Square Problem}\par
\vspace{0.8cm}
{\Large Kelompok A12}\par
\vspace{0.7cm}
\begin{tabular}{ll}
2406402542 & Naufal Zafran Fadil\\
2406429020 & WILLIAM JONNATAN\\
2406437893 & TSANIYA FINI ARDIYANTI\\
2306227311 & Franky Raymarcell Sinaga
\end{tabular}
\end{center}
\vspace{0.7cm}
\noindent\textbf{Pakta integritas}\par\medskip
\noindent Dengan ini, kami menyatakan bahwa tugas ini adalah hasil pekerjaan kelompok sendiri.
\vspace{0.55cm}
\begin{center}
""" + cards[0] + r"\hfill" + cards[1] + r"\par\vspace{0.4cm}" + cards[2] + r"\hfill" + cards[3] + r"""\par
\end{center}
\vspace{0.35cm}
\noindent\textbf{Distribusi kontribusi.} Soal 1 dan Soal 2 masing-masing mencakup 50\% pekerjaan kelompok. Kontribusi total setiap anggota adalah 25\%: Naufal Zafran Fadil 25\%, WILLIAM JONNATAN 25\%, TSANIYA FINI ARDIYANTI 25\%, dan Franky Raymarcell Sinaga 25\%.
\end{document}
"""
    path = OUT / "cover.tex"
    path.write_text(tex, encoding="utf-8")
    return path


def make_soal1() -> Path:
    original = (ROOT / "soal1/report/soal1.tex").read_text(encoding="utf-8")
    preamble, body = original.split(r"\begin{document}", 1)
    body = body.rsplit(r"\end{document}", 1)[0]
    body = body[body.index(r"\setcounter{section}{1}"):]
    body = body.replace(r"\setcounter{section}{1}", "", 1)

    # The group reran its benchmark after drafting the prose. Synchronize the
    # submission copy with the latest CSV, without changing the group's source.
    with (ROOT / "soal1/hasil/benchmark_ringkas.csv").open(newline="", encoding="utf-8") as f:
        bench = {int(row["N"]): row for row in csv.DictReader(f)}
    b512, b2048 = bench[512], bench[2048]
    ratio512 = float(b512["solver_dense_ms"]) / float(b512["solver_band_ms"])
    ratio2048 = float(b2048["solver_dense_ms"]) / float(b2048["solver_band_ms"])
    body = body.replace("8.0 kali", f"{ratio512:.1f} kali")
    body = body.replace("18.8~ms", f'{float(b512["solver_band_ms"]):.1f}~ms')
    body = body.replace("27.1~ms", f'{float(b512["baca_csv_ms"]):.1f}~ms')
    body = body.replace("12.4~s", f'{float(b2048["solver_dense_ms"])/1000:.1f}~s')
    body = body.replace("76~ms", f'{float(b2048["solver_band_ms"]):.0f}~ms')
    body = body.replace("sekitar 160 kali", f"sekitar {ratio2048:.0f} kali")
    body = body.replace(
        "waktu membaca CSV (27.1~ms)",
        f'waktu membaca CSV ({float(b512["baca_csv_ms"]):.1f}~ms)',
    )
    body = body.replace(
        r"\section{Data dan Validasi}\label{sec:data}",
        r"""\section{Pendahuluan}
Distribusi penumpang jangka panjang pada koridor halte dapat dimodelkan sebagai distribusi stasioner rantai Markov. Tujuan studi ini ialah menghitung distribusi tersebut untuk enam matriks transisi kode B milik kelompok genap A12, dan membandingkan solver LU dense dengan solver berpivot parsial yang memanfaatkan struktur pita. Kami memeriksa validitas data, mengatasi singularitas sistem stasioner dengan satu syarat skala, lalu mengukur waktu, memori, kondisi, dan galat. Hasil dipakai untuk menentukan metode yang tepat ketika jumlah halte membesar.\par

\section{Data dan Validasi}\label{sec:data}""",
        1,
    )
    body = body.replace(
        r"\renewcommand{\refname}{Referensi}",
        r"""\section{Kesimpulan}
Enam matriks transisi valid dan menghasilkan distribusi stasioner tunggal. Struktur $B$ memiliki $p=2$ dan $q=1$, sehingga penyimpanan dan eliminasi pita memerlukan ruang dan operasi yang tumbuh linear terhadap $N$ untuk lebar pita tetap. Pada data $N=512$, solver banded memakai 60~KiB dan sekitar 20.1~ms, sedangkan solver dense memakai 4108~KiB dan sekitar 164.2~ms. Kedua solusi memberikan residual stasioner yang praktis identik; pada $N=256$ kondisi sangat besar karena rantai hampir terpisah, sehingga pemeriksaan kondisi tetap penting. Untuk koridor yang panjang, solver banded dengan partial pivoting adalah pilihan utama.\par

\renewcommand{\refname}{Referensi}""",
        1,
    )
    preamble = preamble[: preamble.index(r"\title{")]
    front = r"""\begin{document}
\begin{center}
{\Large\bfseries Soal 1: Analisis Perpindahan Penumpang Antarhalte}\par\medskip
Kelompok A12 -- TK 1 Analisis Numerik
\end{center}
\section*{Rangkuman}
Studi ini menentukan distribusi steady state untuk enam matriks perpindahan penumpang kode B, dengan 16 sampai 512 halte. Karena $I-T^\mathsf{T}$ singular, satu persamaan diganti dengan syarat skala dan solusi dinormalkan. Kami mengimplementasikan LU dense serta eliminasi pita berpivot parsial untuk matriks dengan lower bandwidth 2 dan upper bandwidth 1. Kedua solver memberi solusi dan residual yang sama pada ketelitian eksperimen. Pada $N=512$, solver pita memerlukan 60~KiB dan 20.1~ms, dibandingkan 4108~KiB dan 164.2~ms untuk dense. Kasus $N=256$ hampir terpisah menjadi dua bagian dan menghasilkan kondisi terbesar, $\kappa_1(B)\approx1.71\times10^9$. Halte terakhir memiliki proporsi maksimum pada semua ukuran. Solver pita direkomendasikan untuk koridor besar, sambil tetap memantau kondisi matriks.
\setcounter{tocdepth}{1}
\tableofcontents
\clearpage
"""
    path = ROOT / "soal1/report/submission.tex"
    path.write_text(preamble + front + body + r"\end{document}" + "\n", encoding="utf-8")
    return path


def make_soal2() -> Path:
    original = (ROOT / "soal2/report/main.tex").read_text(encoding="utf-8")
    preamble, body = original.split(r"\begin{document}", 1)
    body = body.rsplit(r"\end{document}", 1)[0]
    body = body[body.index(r"\section{Formulasi matriks desain}"):]
    body = body.replace(
        r"\section{Formulasi matriks desain}",
        r"""\section{Pendahuluan}
Model SETAR dua rezim memprediksi return saham menggunakan dua return terdahulu dan ambang tanda return terakhir. Tujuan studi ini ialah membentuk sistem kuadrat terkecil yang bebas dari kebocoran target, menyelesaikannya dengan persamaan normal dan rotasi Givens sesuai aturan kelompok genap, lalu membandingkan stabilitas dan akurasi pada data latih serta data uji. Analisis juga mencakup biaya komputasi, sensitivitas outlier, interpretasi koefisien, dan grafik prediksi terhadap return aktual.\par

\section{Formulasi matriks desain}""",
        1,
    )
    body = body.replace(r"\section{Pengaruh outlier dan kesimpulan}", r"\section{Pengaruh outlier}", 1)
    body += r"""
\section{Kesimpulan}
Persamaan normal dan Givens menghasilkan solusi yang sama sampai presisi yang dilaporkan: norma residual latih $0.15297705$, RMSE latih $0.00883213$, dan RMSE uji $0.01196708$. Pembentukan $A^\mathsf{T}A$ meningkatkan bilangan kondisi dari $192.61$ menjadi $37096.84$; rotasi Givens karena itu lebih aman terhadap pembulatan bila data menjadi lebih buruk kondisinya. Untuk biaya yang wajar, rotasi diterapkan langsung ke dua baris matriks dan ruas kanan tanpa menyimpan $Q$ eksplisit. Koefisien bullish menunjukkan momentum pada kedua lag, sedangkan koefisien bearish menunjukkan pembalikan dalam model ini; akurasi luar sampel lebih rendah daripada akurasi latih.

\renewcommand{\refname}{Referensi}
\begin{thebibliography}{9}
\bibitem{golub} G. H. Golub dan C. F. Van Loan, \emph{Matrix Computations}, edisi ke-4. Johns Hopkins University Press, 2013, Bab 5 dan Subbab 5.1.8 (Givens rotations).
\bibitem{trefethen} L. N. Trefethen dan D. Bau III, \emph{Numerical Linear Algebra}. SIAM, 1997, Kuliah 11 (least squares), 18 (conditioning of least squares), dan 19 (stability of least squares algorithms).
\bibitem{higham} N. J. Higham, \emph{Accuracy and Stability of Numerical Algorithms}, edisi ke-2. SIAM, 2002, Bab 7 (perturbation theory for linear systems) dan 20 (the least squares problem).
\end{thebibliography}

\appendix
\section{Program Reproduksi}
Program lengkap terdapat pada \texttt{soal2/program.ipynb}; perhitungan ulang dan pembuatan grafik dapat dijalankan melalui \texttt{soal2/report/analyze.py}. Cara menjalankan keduanya dijelaskan dalam \texttt{README.md} paket submisi.\par
"""
    body = body.replace(
        "Untuk menghilangkan entri $a_{ji}$ di bawah diagonal",
        "Rotasi ortogonal menghindari pembentukan matriks normal sehingga lebih tahan terhadap galat pembulatan~\\cite{golub,trefethen,higham}. Untuk menghilangkan entri $a_{ji}$ di bawah diagonal",
        1,
    )
    body = body.replace(
        r"Syarat stasioner $\norm{Ax-b}^{2}$ menghasilkan",
        r"Kondisi optimal kuadrat terkecil untuk matriks desain ber-rank penuh menghasilkan persamaan normal~\cite{trefethen}. Syarat stasioner $\norm{Ax-b}^{2}$ menghasilkan",
        1,
    ).replace(
        "Membentuk persamaan normal karena itu berpotensi memperbesar pengaruh pembulatan",
        "Membentuk persamaan normal karena itu berpotensi memperbesar pengaruh pembulatan~\\cite{higham,trefethen}",
        1,
    )
    old_figure = r"""\begin{figure}[H]
\centering
\includegraphics[width=0.82\textwidth]{figures/overlay.pdf}"""
    new_figure = r"""Gambar~\ref{fig:train-overlay} memperlihatkan return aktual dan prediksi pada data latih. Gambar~\ref{fig:continuous-overlay} menunjukkan segmen uji sebagai kelanjutan kronologis dengan batas yang jelas.

\begin{figure}[H]
\centering
\includegraphics[width=0.82\textwidth]{figures/train_overlay.pdf}
\caption{Return aktual dan prediksi SETAR pada 300 observasi latih.}
\label{fig:train-overlay}
\end{figure}

\begin{figure}[H]
\centering
\includegraphics[width=0.82\textwidth]{figures/overlay.pdf}"""
    assert old_figure in body
    body = body.replace(old_figure, new_figure, 1)
    body = body.replace(
        r"\caption{Return aktual dan prediksi dari model yang dilatih pada segmen kiri. Garis putus-putus menunjukkan batas latih/uji; indeks uji pertama memakai riwayat harga latih.}",
        r"\caption{Return aktual dan prediksi dari model yang dilatih pada segmen kiri. Garis putus-putus menunjukkan batas latih/uji; indeks uji pertama memakai riwayat harga latih.}" + "\n" + r"\label{fig:continuous-overlay}",
        1,
    )
    preamble = preamble[: preamble.index(r"\title{")]
    preamble += r"""\numberwithin{equation}{section}
\counterwithin{table}{section}
\counterwithin{figure}{section}
\counterwithin{algorithm}{section}
\floatname{algorithm}{Kode}
"""
    front = r"""\begin{document}
\begin{center}
{\Large\bfseries Soal 2: Deteksi Rezim Pasar dan Prediksi Return Saham dengan SETAR}\par\medskip
Kelompok A12 -- TK 1 Analisis Numerik
\end{center}
\section*{Rangkuman}
Kami membangun model SETAR dua rezim dan dua lag dari 303 harga penutupan latih, menghasilkan sistem kuadrat terkecil berukuran $300\times6$. Persamaan normal diselesaikan dengan eliminasi Gauss berpivot parsial; metode kedua menggunakan QR rotasi Givens. Koefisien keduanya berbeda hanya $2.44\times10^{-16}$ dalam norma dua. Norma residual latih adalah $0.15297705$, RMSE latih $0.00883213$, dan RMSE uji pada 103 return sambung $0.01196708$. Matriks desain memiliki $\kappa_2(A)=192.61$, sementara matriks normal memiliki $\kappa_2(A^\mathsf{T}A)=37096.84$. Jadi Givens lebih stabil secara numerik, walaupun akurasi empiris keduanya sama pada data ini. Model menunjukkan koefisien lag positif pada rezim bullish dan negatif pada rezim bearish; outlier dapat menggeser parameter dan residual.
\setcounter{tocdepth}{1}
\tableofcontents
\clearpage
"""
    path = ROOT / "soal2/report/submission.tex"
    path.write_text(preamble + front + body + r"\end{document}" + "\n", encoding="utf-8")
    return path


def make_readme() -> Path:
    text = """# TK 1 Analisis Numerik -- Kelompok A12

Satu PDF gabungan (`TK A12 ... .pdf`) memuat sampul dan pakta integritas, laporan Soal 1, lalu laporan Soal 2. Soal 1 menggunakan data kode B karena A12 adalah kelompok genap. Kontribusi total masing-masing anggota adalah 25%; bobot kedua soal masing-masing 50%.

## Menjalankan kode

Gunakan Python 3.12 dengan `numpy`, `pandas`, `matplotlib`, `scipy`, dan `pymupdf`. Buka `soal1/soal1.ipynb` dan `soal2/program.ipynb` pada Jupyter, lalu jalankan **Restart & Run All** di masing-masing notebook. Kedua notebook membaca CSV pada folder masing-masing. Pustaka solver linear hanya digunakan untuk pemeriksaan terpisah pada Soal 1, bukan solusi utama. Hasil Soal 1 tersimpan pada `soal1/hasil/`.

Untuk mereproduksi angka dan dua grafik Soal 2 dari skrip tersendiri, jalankan `python soal2/report/analyze.py`. Setelah hasil Soal 1 berubah, jalankan `python soal1/report/buat_tabel.py` untuk memperbarui tabel LaTeX dari CSV.

## Membangun PDF

Perlu MiKTeX `pdflatex` di PATH. Dari direktori ini, jalankan `python build_submission.py`. Skrip membuat sumber `submission.tex` di kedua folder laporan, mengompilasi sampul dan kedua laporan, lalu menggabungkannya menjadi satu PDF bernama sesuai NPM. Skrip juga membuat ZIP yang bernama sama, berisi PDF, notebook, data, berkas hasil, aset, sumber LaTeX, dan README ini. Berkas `ignore/` hanya berisi gambar tanda tangan yang dipakai pada sampul.
"""
    path = ROOT / "README.md"
    path.write_text(text, encoding="utf-8")
    return path


def make_condition_figure() -> None:
    path = ROOT / "soal1/hasil/kondisi_vs_N.png"
    with (ROOT / "soal1/hasil/kondisi_galat.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.7), constrained_layout=True)
    for kind, marker, linestyle, label in [
        ("data", "o", "-", "Data soal"),
        ("sintetis", "o", "--", "Sintetis"),
    ]:
        chosen = [r for r in rows if r["sumber"] == kind]
        if not chosen:
            continue
        axes[0].loglog([int(r["N"]) for r in chosen], [float(r["kappa1_B"]) for r in chosen],
                       marker=marker, markerfacecolor="none" if kind == "sintetis" else None,
                       linestyle=linestyle, label=label)
        axes[1].loglog([float(r["batas_kappa_u"]) for r in chosen],
                       [float(r["galat_eksak_dense"]) for r in chosen],
                       marker=marker, linestyle="none", markerfacecolor="none" if kind == "sintetis" else None,
                       label=label)
    bounds = [float(r["batas_kappa_u"]) for r in rows]
    axes[1].loglog([min(bounds), max(bounds)], [min(bounds), max(bounds)], "k--", lw=1, label=r"$\delta=\kappa_1\epsilon$")
    axes[0].set(xlabel="Jumlah halte N", ylabel=r"$\kappa_1(B)$")
    axes[1].set(xlabel=r"$\kappa_1(B)\epsilon$", ylabel=r"Galat maju eksak $\delta$")
    for ax in axes:
        ax.grid(True, which="both", alpha=0.25)
        ax.legend(fontsize=8)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    (ROOT / "soal1/report/buat_tabel.py").exists() or (_ for _ in ()).throw(FileNotFoundError())
    subprocess.run(["python", "buat_tabel.py"], cwd=ROOT / "soal1/report", check=True)
    make_condition_figure()
    subprocess.run(["python", "analyze.py"], cwd=ROOT / "soal2/report", check=True, stdout=subprocess.DEVNULL)
    source_cover = make_cover()
    source_one = make_soal1()
    source_two = make_soal2()
    make_readme()
    pdfs = [
        run_latex(source_cover, BUILD / "cover"),
        run_latex(source_one, BUILD / "soal1"),
        run_latex(source_two, BUILD / "soal2"),
    ]
    combined = pymupdf.open()
    for pdf in pdfs:
        with pymupdf.open(pdf) as part:
            combined.insert_pdf(part)
    pdf_path = OUT / f"{STEM}.pdf"
    combined.save(pdf_path, garbage=4, deflate=True)
    combined.close()

    include = [
        ROOT / "README.md",
        ROOT / "build_submission.py",
        OUT / "cover.tex",
        pdf_path,
    ]
    for directory in ["soal1/dataset", "soal1/hasil", "soal1/report/generated", "soal2/report/figures", "ignore"]:
        include.extend(p for p in (ROOT / directory).rglob("*") if p.is_file())
    for name in [
        "soal1/soal1.ipynb", "soal1/report/soal1.tex", "soal1/report/submission.tex",
        "soal1/report/buat_tabel.py", "soal2/program.ipynb", "soal2/stock_train.csv",
        "soal2/stock_test.csv", "soal2/report/main.tex", "soal2/report/submission.tex",
        "soal2/report/analyze.py", "soal2/report/metrics.json",
    ]:
        include.append(ROOT / name)
    zip_path = OUT / f"{STEM}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(set(include)):
            archive.write(file, file.relative_to(ROOT))
    print(f"PDF: {pdf_path} ({len(pymupdf.open(pdf_path))} pages)")
    print(f"ZIP: {zip_path}")


if __name__ == "__main__":
    main()
