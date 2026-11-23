# PilihPewangi SPK (Weighted Product)

Aplikasi Streamlit untuk memilih pewangi setrika terfavorit dengan metode Weighted Product.
Kasus Sukmajaya Laundry, berdasarkan Nurizki & Farkhatin (2024),
Jurnal Ilmiah Sains Teknologi dan Informasi 2(4), 1-10.

## Menjalankan di komputer
    pip install -r requirements.txt
    streamlit run app.py

## Deploy ke Streamlit Community Cloud
1. Buat repositori GitHub baru, lalu unggah `app.py`, `wp_engine.py`, `requirements.txt`, dan folder `.streamlit`.
2. Buka https://share.streamlit.io dan masuk dengan akun GitHub.
3. Pilih "Create app", isi repositori, branch, dan Main file path `app.py`, lalu Deploy.

## Struktur
- `app.py`             : tampilan Streamlit (4 tab: Data, Bobot & Jenis Kriteria, Perhitungan, Hasil)
- `wp_engine.py`       : perhitungan WP (tanpa Streamlit)
- `test_wp_engine.py`  : 14 pengujian otomatis; jalankan dengan `pytest`
- `.streamlit/config.toml` : tema warna

## Catatan
- Data awal adalah data dari jurnal. Jurnal tidak menjelaskan arti skala nilai 1 sampai 3.
- Jurnal menganggap semua kriteria benefit. Jenis tiap kriteria dapat diubah di tab Bobot & Jenis Kriteria.
