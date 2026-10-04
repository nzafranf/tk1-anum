# TK 1 Analisis Numerik -- Kelompok A12

Satu PDF gabungan (`TK A12 ... .pdf`) memuat sampul dan pakta integritas, satu daftar isi, laporan Soal 1 dan Soal 2, serta satu daftar referensi. Soal 1 menggunakan data kode B karena A12 adalah kelompok genap. Kontribusi total masing-masing anggota adalah 25%; bobot kedua soal masing-masing 50%.

ZIP memuat kedua notebook, seluruh CSV input, grafik dan tabel hasil, skrip reproduksi, sumber LaTeX, gambar tanda tangan, dan PDF akhir.

## Menjalankan kode

Gunakan Python 3.12 dengan `numpy`, `pandas`, `matplotlib`, `scipy`, dan `pymupdf`. Buka `soal1/soal1.ipynb` dan `soal2/program.ipynb` pada Jupyter, lalu jalankan **Restart & Run All** di masing-masing notebook. Kedua notebook membaca CSV pada folder masing-masing. Pustaka solver linear hanya digunakan untuk pemeriksaan terpisah pada Soal 1, bukan solusi utama. Hasil Soal 1 tersimpan pada `soal1/hasil/`.

Untuk mereproduksi angka dan tiga grafik Soal 2 dari skrip tersendiri, jalankan `python soal2/report/analyze.py`. Setelah hasil Soal 1 berubah, jalankan `python soal1/report/buat_tabel.py` untuk memperbarui tabel LaTeX dari CSV.

## Membangun PDF

Perlu MiKTeX `pdflatex` di PATH. Dari direktori ini, jalankan `python build_final.py`. Skrip mengompilasi sampul dan dokumen gabungan, lalu membuat PDF dan ZIP bernama sesuai NPM. Berkas `ignore/` berisi gambar tanda tangan yang dipakai pada sampul.
