import numpy as np
import pandas as pd
from wp_engine import *


def hasil(data=DATA_JURNAL, bobot=BOBOT_JURNAL, jenis=JENIS_JURNAL):
    return hitung(data, bobot, jenis)


def test_U01_U02_data_jurnal():
    r = hasil()
    h = r["hasil"]
    assert h.loc[0, "Pewangi"] == "Sakura" and round(h.loc[0, "Nilai (V)"], 4) == 0.1745
    assert round(h.loc[0, "Nilai (V)"], 9) == 0.174458552            # sama dengan jurnal
    assert round(r["s"].sum(), 4) == 14.3281 and round(r["v"].sum(), 9) == 1.0


def test_vektor_s_dan_v_sama_dengan_jurnal():
    s_jurnal = [1.610763153, 2.499655669, 1.414213562, 1.40225077, 2.047672511, 1.551845574, 2.119883526, 1.681792831]
    v_jurnal = [0.112420047, 0.174458552, 0.098702255, 0.097867335, 0.142913276, 0.10830801, 0.147953102, 0.117377423]
    r = hasil()
    assert np.allclose(r["s"], s_jurnal, atol=1e-8) and np.allclose(r["v"], v_jurnal, atol=1e-8)


def test_urutan_peringkat_jurnal():
    assert list(hasil()["hasil"]["Pewangi"]) == ["Sakura", "Glamorous", "Florist", "Soft Jasmine", "Ocean Fresh", "Passion", "Blossom Red", "Sweety"]


def test_U03_bobot_sama():
    h = hasil(bobot=[1] * 5)["hasil"]
    assert h.loc[0, "Pewangi"] == "Sakura" and round(h.loc[0, "Nilai (V)"], 4) == 0.1756


def test_U04_alkohol_cost():
    h = hasil(jenis=["benefit", "benefit", "cost", "benefit", "benefit"])["hasil"]
    assert h.loc[0, "Pewangi"] == "Florist" and round(h.loc[0, "Nilai (V)"], 4) == 0.1697
    assert round(h["Nilai (V)"].sum(), 9) == 1.0


def test_U05_hapus_sakura():
    d = DATA_JURNAL[DATA_JURNAL["Pewangi"] != "Sakura"].reset_index(drop=True)
    h = hasil(d)["hasil"]
    assert h.loc[0, "Pewangi"] == "Glamorous" and round(h.loc[0, "Nilai (V)"], 4) == 0.1792


def test_U06_bobot_nol():
    assert any("Total bobot masih 0" in g for g in validasi(DATA_JURNAL, [0] * 5))


def test_U07_nilai_nol():
    d = DATA_JURNAL.copy(); d.loc[0, "Varian Aroma"] = 0
    assert any("minimal 1" in g for g in validasi(d, BOBOT_JURNAL))


def test_U08_nama_kembar():
    d = DATA_JURNAL.copy(); d.loc[1, "Pewangi"] = "ocean fresh"
    assert any("kembar" in g for g in validasi(d, BOBOT_JURNAL))


def test_U09_satu_pewangi():
    assert any("Minimal ada 2" in g for g in validasi(DATA_JURNAL.head(1), BOBOT_JURNAL))


def test_U10_seri_di_peringkat_satu():
    d = DATA_JURNAL.head(2).copy()
    d.iloc[1, 1:] = d.iloc[0, 1:].values
    h = hasil(d)["hasil"]
    assert set(h["Status"]) == {"SERI TERBAIK"} and (h["Peringkat"] == 1).all()


def test_validasi_aman_dan_nilai_kosong():
    assert validasi(DATA_JURNAL, BOBOT_JURNAL) == []
    d = DATA_JURNAL.copy(); d.loc[2, "Persediaan Stok"] = None
    assert validasi(d, BOBOT_JURNAL)


def test_dominan_dan_skenario():
    assert dominan(DATA_JURNAL, JENIS_JURNAL) == ["Sakura"]                 # Sakura tertinggi di semua kriteria
    assert dominan(DATA_JURNAL, ["benefit", "benefit", "cost", "benefit", "benefit"]) == []
    sk = skenario(DATA_JURNAL, BOBOT_JURNAL, JENIS_JURNAL)
    assert sk.loc[0, "Peringkat 1"] == "Sakura"
    assert sk[sk["Skenario"].str.startswith("Kandungan Alkohol")]["Peringkat 1"].iloc[0] == "Florist"
    assert sk[sk["Skenario"] == "Semua bobot disamakan"]["Peringkat 1"].iloc[0] == "Sakura"


def test_bobot_nol_pada_satu_kriteria_tidak_error():
    h = hasil(bobot=[5, 5, 0, 3, 3])["hasil"]
    assert h["Nilai (V)"].notna().all() and round(h["Nilai (V)"].sum(), 9) == 1.0
