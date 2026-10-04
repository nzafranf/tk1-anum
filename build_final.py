"""Compile one TK1 report with one contents page and one bibliography; package code.

Run from the project root: python build_final.py
"""

import ast
import json
from pathlib import Path
import subprocess
import zipfile

import pymupdf


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "submission"
BUILD = OUT / "build" / "final"
STEM = "TK1_A12_2406402542_2406429020_2406437893_2306227311"


def make_code_excerpts() -> None:
    notebook = json.loads((ROOT / "soal1/soal1.ipynb").read_text(encoding="utf-8"))
    soal1_functions = {}
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"])
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in {"lu_dense", "lu_band"}:
                soal1_functions[node.name] = ast.get_source_segment(source, node)
    if set(soal1_functions) != {"lu_dense", "lu_band"}:
        raise ValueError("Core Soal 1 solver functions were not found")
    s1 = "# Extracted verbatim from soal1/soal1.ipynb\nimport numpy as np\n\n"
    s1 += soal1_functions["lu_dense"] + "\n\n" + soal1_functions["lu_band"] + "\n"
    (OUT / "code_soal1.py").write_text(s1, encoding="utf-8")

    source = (ROOT / "soal2/report/analyze.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {
        node.name: ast.get_source_segment(source, node)
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in {"gaussian_pivot", "givens_least_squares"}
    }
    if set(functions) != {"gaussian_pivot", "givens_least_squares"}:
        raise ValueError("Core Soal 2 solver functions were not found")
    s2 = "# Extracted verbatim from soal2/report/analyze.py\nimport numpy as np\n\n"
    s2 += functions["gaussian_pivot"] + "\n\n" + functions["givens_least_squares"] + "\n"
    (OUT / "code_soal2.py").write_text(s2, encoding="utf-8")


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
\usepackage{algorithm,algpseudocode,listings}
\usepackage[hidelinks]{hyperref}
\geometry{margin=2.54cm}
\emergencystretch=1em
\numberwithin{equation}{section}
\counterwithin{table}{section}
\counterwithin{figure}{section}
\counterwithin{algorithm}{section}
\floatname{algorithm}{Kode}
\renewcommand{\lstlistingname}{Kode}
\algrenewcommand\algorithmicrequire{\textbf{Masukan:}}
\algrenewcommand\algorithmicensure{\textbf{Keluaran:}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\norm}[1]{\left\lVert #1\right\rVert_2}
\lstset{language=Python,basicstyle=\ttfamily\footnotesize,breaklines=true,
  columns=fullflexible,keepspaces=true,showstringspaces=false,frame=single}
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
\clearpage
\appendix
\renewcommand{\thelstlisting}{A.\arabic{lstlisting}}
\section{Lampiran: Verifikasi dan Rincian Reproduksi}
\subsection{Uji solver untuk Soal 1}
Sebagai uji terukur bagi faktor LU dan permutasi, digunakan
\[
B=\begin{pmatrix}2&1&1\\4&3&3\\8&7&9\end{pmatrix},\qquad
b=\begin{pmatrix}3\\7\\19\end{pmatrix}.
\]
Baris ketiga dipilih sebagai pivot pertama. Dengan urutan baris akhir $(3,1,2)$, kedua implementasi menghasilkan
\[
L=\begin{pmatrix}1&0&0\\1/4&1&0\\1/2&2/3&1\end{pmatrix},\qquad
U=\begin{pmatrix}8&7&9\\0&-3/4&-5/4\\0&0&-2/3\end{pmatrix}.
\]
Perkalian langsung memberi $PB=LU$ dan penyelesaian menghasilkan $z=(1,-1,2)^\mathsf{T}$. Pada uji terpisah, matriks pita $8\times8$ dengan $p=2,q=1$ dan diagonal yang diperkecil 100 kali memicu tujuh pertukaran baris serta delapan elemen \emph{fill-in}; faktor $U$ melebar hingga upper bandwidth $p+q=3$. Ini memeriksa jalur pivot yang tidak terpakai oleh keenam data soal. Pada rantai tiga halte dengan distribusi acuan $(1/4,1/2,1/4)^\mathsf{T}$, kedua solver mengembalikan distribusi tersebut. Uji matriks singular $\left(\begin{smallmatrix}1&2\\2&4\end{smallmatrix}\right)$ ditolak karena pivot akhirnya nol.

\subsection{Nilai rinci dan rotasi pertama untuk Soal 2}
Ada 303 harga latih yang menghasilkan 302 return; setelah dua lag, matriks desain mempunyai 300 baris. Segmen uji mempunyai 103 harga dan 103 return karena return pertama memakai harga penutupan terakhir dari segmen latih. Untuk dua baris pertama desain, $a_{11}=0$ dan $a_{21}=1$, sehingga rotasi pertama mempunyai $c=0$, $s=1$ dan blok $\left(\begin{smallmatrix}0&1\\-1&0\end{smallmatrix}\right)$. Setelah $G_1$ diterapkan, entri $(2,1)$ tepat nol; baris lain tidak berubah pada langkah ini.
\begin{table}[H]\centering\small
\caption{Koefisien SETAR dari QR Givens sebelum pembulatan laporan.}\label{tab:appendix-coeff}
\begin{tabular}{lr}\toprule
Parameter & Nilai\\\midrule
$\alpha_1$ & $0.001513374224392619$\\
$\phi_{1,1}$ & $0.17215289727492178$\\
$\phi_{1,2}$ & $0.16607285095297825$\\
$\alpha_2$ & $-0.0012126885538670722$\\
$\phi_{2,1}$ & $-0.3603768239374077$\\
$\phi_{2,2}$ & $-0.10980803854712604$\\\bottomrule
\end{tabular}\end{table}
Tabel~\ref{tab:appendix-coeff} memuat nilai yang digunakan untuk prediksi tanpa membulatkan koefisien terlebih dahulu. Selisih norma dua antara koefisien persamaan normal dan Givens ialah $2.43949\times10^{-16}$. ZIP submisi menyertakan kedua notebook, delapan CSV input, keluaran eksperimen, dan README dengan langkah menjalankan ulang program.
\clearpage
\subsection{Kode inti dari implementasi}
Kode~\ref{code:soal1} menampilkan bagian faktorisasi kedua solver pada Soal 1. Substitusi segitiga dan normalisasi telah dijabarkan pada Kode~\ref{alg:soal1-solvers}; implementasi lengkap disertakan dalam notebook. Kode~\ref{code:soal2} menampilkan solver persamaan normal dan Givens dari skrip reproduksi Soal 2. Rotasi diterapkan langsung pada dua baris matriks kerja dan ruas kanan, lalu diakhiri substitusi balik.
\lstinputlisting[caption={Faktorisasi LU dense dan pita pada Soal 1.},label={code:soal1}]{code_soal1.py}
\clearpage
\lstinputlisting[caption={Solver Gauss berpivot dan QR Givens pada Soal 2.},label={code:soal2}]{code_soal2.py}
\end{document}
"""
    path = OUT / "combined.tex"
    path.write_text(preamble + s2 + bib, encoding="utf-8")
    return path


def package(pdf: Path) -> Path:
    paths = [
        ROOT / "README.md",
        ROOT / "soal1/soal1.ipynb", ROOT / "soal2/program.ipynb",
        ROOT / "soal2/stock_train.csv", ROOT / "soal2/stock_test.csv",
        ROOT / "soal2/report/analyze.py", ROOT / "soal2/report/metrics.json",
        ROOT / "soal1/report/buat_tabel.py",
    ]
    for directory in ["soal1/dataset", "soal1/hasil", "soal2/report/figures"]:
        paths.extend(p for p in (ROOT / directory).rglob("*") if p.is_file())
    archive_path = OUT / (STEM + ".zip")
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(pdf, pdf.name)
        for path in sorted(set(paths)):
            archive.write(path, path.relative_to(ROOT))
    return archive_path


def main() -> None:
    make_code_excerpts()
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
