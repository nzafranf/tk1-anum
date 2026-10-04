# TK 1 Analisis Numerik -- Kelompok A12

**Mulai dari PDF `TK1_A12_2406402542_2406429020_2406437893_2306227311.pdf` di tingkat teratas ZIP.** PDF itu adalah laporan gabungan untuk kedua soal. Soal 1 memakai data kode B karena A12 adalah kelompok genap.

ZIP berisi dua folder kerja yang terpisah:

- `soal1/`: notebook `soal1.ipynb`, enam CSV input di `dataset/`, dan hasil tabel/grafik di `hasil/`.
- `soal2/`: notebook `program.ipynb`, kedua CSV saham, dan skrip reproduksi `report/analyze.py` beserta grafik dan metrik yang dihasilkan.

## Menjalankan kode

Gunakan Python 3.12 dengan `numpy`, `pandas`, `matplotlib`, `scipy`, dan Jupyter. Masuk ke folder `soal1/`, buka `soal1.ipynb`, lalu jalankan **Restart & Run All**. Ulangi dari folder `soal2/` untuk `program.ipynb`. Kedua notebook membaca CSV pada folder masing-masing. Pustaka solver linear hanya digunakan untuk pemeriksaan terpisah pada Soal 1, bukan solusi utama.

Untuk mereproduksi angka dan tiga grafik Soal 2 dari skrip tersendiri, jalankan `python soal2/report/analyze.py` dari tingkat teratas ZIP. Setelah hasil Soal 1 berubah, jalankan `python soal1/report/buat_tabel.py` untuk memperbarui tabel LaTeX dari CSV hasil.
