"""Compile one TK1 report with one contents page and one bibliography; package code.

Run from the project root: python build_final.py
"""

from pathlib import Path
import subprocess
import zipfile

import pymupdf


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "submission"
BUILD = OUT / "build" / "final"
STEM = "TK A12 2406402542 2406429020 2406437893 2306227311"


def latex(path: Path, build_dir: Path) -> Path:
    build_dir.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        command = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={build_dir}", path.name]
        subprocess.run(command, cwd=path.parent, check=True, stdout=subprocess.DEVNULL)
    return build_dir / (path.stem + ".pdf")


def make_combined_tex() -> Path:
    # The Soal 2 content is the group report, with its old independent front and
    # bibliography removed. The combined document supplies one front and one bib.
    s2 = (ROOT / "soal2/report/submission.tex").read_text(encoding="utf-8")
    s2 = s2[s2.index(r"\section{Pendahuluan}") : s2.index(r"\renewcommand{\refname}{Referensi}")]
    s2 = s2.replace("{figures/", "{../soal2/report/figures/")
    s2 = s2.replace(
        "Biaya Givens berlaku untuk pembaruan dua baris; RMSE uji memakai 103 return sambung.",
        "Biaya Givens berlaku untuk rotasi dua baris langsung, sedangkan implementasi yang membentuk $Q$ eksplisit memerlukan biaya tambahan; RMSE uji memakai 103 return sambung.",
    )
    s2 = s2.replace(
        "konsisten dengan sifat kuadrat terkecil yang sensitif terhadap titik berleverage tinggi.",
        "konsisten dengan sensitivitas kuadrat terkecil terhadap observasi ekstrem.",
    )
    s2 = s2.replace(
        "menandakan efek pembalikan berlanjut hingga dua hari.",
        "menyatakan pengaruh berlawanan arah terhadap return dua hari sebelumnya; arah kontribusi aktual bergantung pada tanda lag tersebut.",
    )
    s2 = s2.replace(
        r"\caption{Residual prediksi per observasi. Beberapa deviasi besar tetap muncul walaupun parameter diperoleh dengan meminimalkan jumlah kuadrat galat latih.}",
        r"\caption{Residual prediksi per observasi. Beberapa deviasi besar tetap muncul walaupun parameter diperoleh dengan meminimalkan jumlah kuadrat galat latih.}" + "\n" + r"\label{fig:residual}",
    )
    s2 = s2.replace(
        r"\caption{Sensitivitas terhadap outlier. Koefisien diestimasi ulang tanpa observasi berresidual terbesar.}",
        r"\caption{Sensitivitas terhadap outlier. Koefisien diestimasi ulang tanpa observasi berresidual terbesar.}" + "\n" + r"\label{tab:outlier}",
    )
    s2 = s2.replace(
        r"\section{Pengaruh outlier}",
        r"\section{Pengaruh outlier}" + "\n" + r"Gambar~\ref{fig:residual} memperlihatkan galat per observasi, sedangkan Tabel~\ref{tab:outlier} mengukur perubahan setelah observasi ekstrem dihapus.",
        1,
    )
    preamble = r"""\documentclass[12pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[indonesian]{babel}
\usepackage{lmodern,geometry,graphicx,booktabs,array,float,microtype}
\usepackage{amsmath,amssymb}
\usepackage{algorithm,algpseudocode}
\usepackage[hidelinks]{hyperref}
\geometry{margin=2.54cm}
\emergencystretch=1em
\numberwithin{equation}{section}
\counterwithin{table}{section}
\counterwithin{figure}{section}
\counterwithin{algorithm}{section}
\floatname{algorithm}{Kode}
\algrenewcommand\algorithmicrequire{\textbf{Masukan:}}
\algrenewcommand\algorithmicensure{\textbf{Keluaran:}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\norm}[1]{\left\lVert #1\right\rVert_2}
\begin{document}
\setcounter{page}{2}
\begin{center}
{\large\bfseries TK 1: Sistem Persamaan Linear dan Least Square Problem}\par\medskip
Kelompok A12 -- Semester Gasal 2026/2027
\end{center}
\setcounter{tocdepth}{1}
\tableofcontents
\clearpage
\input{soal1_condensed.tex}
\clearpage
\begin{center}{\large\bfseries Laporan 2: Model SETAR untuk Prediksi Return Saham}\end{center}
\addcontentsline{toc}{part}{Laporan 2: Model SETAR untuk Prediksi Return Saham}
\setcounter{section}{0}
\section*{Rangkuman}
Kami membangun model SETAR dua rezim dan dua lag dari 303 harga penutupan latih, menghasilkan sistem kuadrat terkecil $300\times6$. Persamaan normal diselesaikan dengan eliminasi Gauss berpivot parsial dan metode kedua dengan QR rotasi Givens. Koefisien kedua metode berbeda $2.44\times10^{-16}$ dalam norma dua; norma residual latih $0.15297705$, RMSE latih $0.00883213$, dan RMSE uji pada 103 return sambung $0.01196708$. Bilangan kondisi $\kappa_2(A)=192.61$ meningkat menjadi $\kappa_2(A^\mathsf{T}A)=37096.84$ pada persamaan normal. Givens lebih tahan terhadap pembulatan, meski akurasi empiris kedua metode sama pada data ini. Koefisien bullish menunjukkan momentum pada kedua lag, sedangkan koefisien bearish menunjukkan pembalikan; outlier dapat menggeser parameter dan residual.
"""
    bib = r"""
\noindent\textbf{Reproduksibilitas.} Seluruh langkah komputasi telah dijelaskan dalam dua laporan ini. Program yang digunakan adalah \texttt{soal1/soal1.ipynb} dan \texttt{soal2/program.ipynb}; skrip \texttt{soal2/report/analyze.py} mengulang perhitungan dan grafik SETAR. Ketiganya beserta CSV input dan README disertakan dalam ZIP submisi.

\clearpage
\renewcommand{\refname}{Referensi}
\begin{thebibliography}{9}
\bibitem{norris} J. R. Norris, \emph{Markov Chains}. Cambridge University Press, 1997, Bab 1.3 dan 1.7--1.8.\par
\bibitem{stewart} W. J. Stewart, \emph{Introduction to the Numerical Solution of Markov Chains}. Princeton University Press, 1994.\par
\bibitem{heath} M. T. Heath, \emph{Scientific Computing: An Introductory Survey}, edisi ke-2. McGraw-Hill, 2002, Bab 1--2.\par
\bibitem{lapack} E. Anderson dkk., \emph{LAPACK Users' Guide}, edisi ke-3. SIAM, 1999.\par
\bibitem{gth} W. K. Grassmann, M. I. Taksar, dan D. P. Heyman, ``Regenerative analysis and steady state distributions for Markov chains,'' \emph{Operations Research}, vol. 33, no. 5, hlm. 1107--1116, 1985.\par
\bibitem{golub} G. H. Golub dan C. F. Van Loan, \emph{Matrix Computations}, edisi ke-4. Johns Hopkins University Press, 2013, Bab 5 dan Subbab 5.1.8 (Givens rotations).\par
\bibitem{trefethen} L. N. Trefethen dan D. Bau III, \emph{Numerical Linear Algebra}. SIAM, 1997, Kuliah 11 (least squares), 18 (conditioning of least squares), dan 19 (stability of least squares algorithms).\par
\bibitem{higham} N. J. Higham, \emph{Accuracy and Stability of Numerical Algorithms}, edisi ke-2. SIAM, 2002, Bab 7 dan 20.\par
\end{thebibliography}
\end{document}
"""
    path = OUT / "combined.tex"
    path.write_text(preamble + s2 + bib, encoding="utf-8")
    return path


def package(pdf: Path) -> Path:
    paths = [
        ROOT / "README.md", ROOT / "build_final.py", OUT / "combined.tex",
        OUT / "soal1_condensed.tex", OUT / "cover.tex", pdf,
        ROOT / "soal1/soal1.ipynb", ROOT / "soal2/program.ipynb",
        ROOT / "soal2/stock_train.csv", ROOT / "soal2/stock_test.csv",
        ROOT / "soal2/report/analyze.py", ROOT / "soal2/report/metrics.json",
        ROOT / "soal1/report/buat_tabel.py", ROOT / "soal2/report/submission.tex",
    ]
    for directory in ["soal1/dataset", "soal1/hasil", "soal2/report/figures", "ignore"]:
        paths.extend(p for p in (ROOT / directory).rglob("*") if p.is_file())
    archive_path = OUT / (STEM + ".zip")
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(paths)):
            archive.write(path, path.relative_to(ROOT))
    return archive_path


def main() -> None:
    combined_source = make_combined_tex()
    cover_pdf = latex(OUT / "cover.tex", BUILD / "cover")
    body_pdf = latex(combined_source, BUILD / "body")
    output_path = OUT / (STEM + ".pdf")
    with pymupdf.open() as output:
        for part_path in [cover_pdf, body_pdf]:
            with pymupdf.open(part_path) as part:
                output.insert_pdf(part)
        output.save(output_path, garbage=4, deflate=True)
    archive = package(output_path)
    print(f"PDF: {output_path} ({len(pymupdf.open(output_path))} pages)")
    print(f"ZIP: {archive}")


if __name__ == "__main__":
    main()
