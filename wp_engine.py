"""Mesin hitung SPK pemilihan pewangi setrika dengan metode Weighted Product (WP).

Kasus Sukmajaya Laundry, berdasarkan Nurizki & Farkhatin (2024),
Jurnal Ilmiah Sains Teknologi dan Informasi 2(4), 1-10.
Fungsi di sini murni perhitungan (tanpa Streamlit) supaya mudah diuji.

Rumus:
    Wj = wj / jumlah(w)                      (normalisasi bobot)
    Si = hasil kali dari xij ^ (+Wj)         untuk kriteria benefit
                          xij ^ (-Wj)        untuk kriteria cost
    Vi = Si / jumlah(S)
"""
import numpy as np
import pandas as pd

KRITERIA = ["Intensitas Aroma", "Kualitas Pewangi", "Kandungan Alkohol", "Persediaan Stok", "Varian Aroma"]
KODE = ["C1", "C2", "C3", "C4", "C5"]
BOBOT_JURNAL = [5, 5, 4, 3, 3]            # Tabel 1 jurnal (skala kepentingan 1-5)
JENIS_JURNAL = ["benefit"] * 5            # jurnal menganggap semua kriteria benefit
SKALA_BOBOT = {0: "Diabaikan", 1: "Tidak penting", 2: "Kurang penting", 3: "Cukup penting", 4: "Penting", 5: "Sangat penting"}

# Data jurnal (Tabel 4). Skala nilai 1-3; artinya tidak dijelaskan jurnal.
DATA_JURNAL = pd.DataFrame({
    "Pewangi": ["Ocean Fresh", "Sakura", "Blossom Red", "Sweety", "Florist", "Passion", "Glamorous", "Soft Jasmine"],
    "Intensitas Aroma": [1, 2, 1, 2, 2, 1, 2, 2],
    "Kualitas Pewangi": [2, 3, 1, 1, 3, 3, 3, 1],
    "Kandungan Alkohol": [2, 2, 2, 1, 1, 1, 2, 2],
    "Persediaan Stok": [1, 3, 2, 3, 3, 1, 3, 2],
    "Varian Aroma": [3, 3, 2, 1, 2, 3, 1, 2],
})


def validasi(data: pd.DataFrame, bobot) -> list:
    """Daftar pesan kesalahan (kosong jika data dan bobot aman)."""
    galat = []
    if len(data) < 2:
        return ["Minimal ada 2 pewangi untuk dibandingkan."]
    nama = data["Pewangi"].astype(str).str.strip()
    if data["Pewangi"].isna().any() or (nama == "").any():
        galat.append("Nama pewangi tidak boleh kosong.")
    elif nama.str.lower().duplicated().any():
        galat.append("Nama pewangi tidak boleh kembar.")
    nilai = data[KRITERIA].apply(pd.to_numeric, errors="coerce")
    if nilai.isna().any().any():
        galat.append("Masih ada nilai yang kosong atau bukan angka. Lengkapi semua nilai.")
    elif (nilai < 1).any().any():
        galat.append("Nilai harus minimal 1, karena WP memerlukan nilai positif.")
    if any(b < 0 for b in bobot):
        galat.append("Bobot tidak boleh negatif.")
    elif sum(bobot) <= 0:
        galat.append("Total bobot masih 0. Naikkan bobot minimal satu kriteria.")
    return galat


def hitung(data: pd.DataFrame, bobot, jenis) -> dict:
    """WP lengkap. `bobot` berisi 5 bilangan >= 0, `jenis` berisi 'benefit' atau 'cost'."""
    x = data[KRITERIA].to_numpy(dtype=float)
    w = np.array(bobot, dtype=float)
    wn = w / w.sum()
    pangkat = wn * np.where(np.array(jenis) == "cost", -1.0, 1.0)
    f = x ** pangkat
    s = f.prod(axis=1)
    v = s / s.sum()
    hasil = pd.DataFrame({"Pewangi": data["Pewangi"].astype(str).str.strip().values, "Vektor S": s, "Nilai (V)": v})
    hasil["Peringkat"] = hasil["Nilai (V)"].round(9).rank(ascending=False, method="dense").astype(int)
    seri = hasil["Peringkat"].duplicated(keep=False)
    hasil["Status"] = np.where(hasil["Peringkat"] == 1, np.where(seri, "SERI TERBAIK", "TERBAIK"),
                               np.where(seri, "SERI", "-"))
    hasil = hasil.sort_values("Peringkat", kind="stable").reset_index(drop=True)
    hasil = hasil[["Peringkat", "Pewangi", "Vektor S", "Nilai (V)", "Status"]]
    return {"x": x, "w": w, "wn": wn, "pangkat": pangkat, "f": f, "s": s, "v": v, "hasil": hasil}


def dominan(data: pd.DataFrame, jenis) -> list:
    """Nama pewangi yang nilainya sama dengan nilai terbaik di SEMUA kriteria.

    Terbaik = nilai terbesar untuk benefit, nilai terkecil untuk cost. Jika ada,
    pemenangnya tidak bergantung pada bobot."""
    x = data[KRITERIA].to_numpy(dtype=float)
    terbaik = np.where(np.array(jenis) == "cost", x.min(axis=0), x.max(axis=0))
    ok = (x == terbaik).all(axis=1)
    return list(data["Pewangi"].astype(str).str.strip()[ok])


def skenario(data: pd.DataFrame, bobot, jenis) -> pd.DataFrame:
    """Bandingkan pemenang pada pengaturan saat ini, bobot sama, dan tiap jenis kriteria dibalik."""
    daftar = [("Pengaturan saat ini", bobot, list(jenis))]
    daftar.append(("Semua bobot disamakan", [1] * 5, list(jenis)))
    for j, k in enumerate(KRITERIA):
        jn = list(jenis)
        jn[j] = "benefit" if jn[j] == "cost" else "cost"
        daftar.append((f"{k} diubah menjadi {jn[j]}", bobot, jn))
    baris = []
    ref = None
    for nama, w, jn in daftar:
        h = hitung(data, w, jn)["hasil"]
        puncak = h[h["Peringkat"] == 1]
        pem = " & ".join(puncak["Pewangi"])
        if ref is None:
            ref = pem
        baris.append({"Skenario": nama, "Peringkat 1": pem, "Nilai (V)": float(puncak["Nilai (V)"].iloc[0]),
                      "Sama dengan pengaturan saat ini": "Ya" if pem == ref else "Tidak"})
    return pd.DataFrame(baris)
