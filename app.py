import pandas as pd
import streamlit as st

import wp_engine as wp

st.set_page_config(page_title="PilihPewangi SPK", page_icon="🧺", layout="centered")

st.markdown("""
<style>
.banner{background:linear-gradient(135deg,#0B4F5C 0%,#0E7C86 100%);color:#fff;padding:26px 28px;border-radius:16px;margin-bottom:18px}
.banner h1{margin:0;font-size:1.9rem;color:#fff}.banner p{margin:6px 0 0;opacity:.92;font-size:.95rem}
.rekom{border:2px solid #0E7C86;background:#E6F4F5;border-radius:14px;padding:18px;text-align:center;margin:8px 0 14px}
.rekom small{letter-spacing:.08em;font-weight:700;color:#0B4F5C}.rekom h2{margin:4px 0;color:#0B4F5C}
.rekom.seri{border-color:#C98B00;background:#FFF6DD}
div[data-testid="stTabs"] button{font-weight:600}
</style>
<div class="banner"><h1>🧺 PilihPewangi SPK</h1>
<p>Sistem Pendukung Keputusan pemilihan pewangi setrika terfavorit dengan metode Weighted Product (WP).<br>
Kasus Sukmajaya Laundry, berdasarkan Nurizki &amp; Farkhatin (2024).</p></div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------ state awal
if "data" not in st.session_state:
    st.session_state["data"] = wp.DATA_JURNAL.copy()
for j in range(5):
    st.session_state.setdefault(f"bobot{j}", wp.BOBOT_JURNAL[j])
    st.session_state.setdefault(f"jenis{j}", "Benefit")

tab_data, tab_bobot, tab_hitung, tab_hasil = st.tabs(["Data", "Bobot & Jenis Kriteria", "Perhitungan", "Hasil"])

# ------------------------------------------------------------ data
with tab_data:
    st.subheader("Data Pewangi Setrika")
    st.caption("Klik dua kali sebuah sel untuk mengubah nilainya. Tambah baris di bagian bawah tabel atau hapus baris yang "
               "tidak perlu. Data awal adalah data dari jurnal.")
    with st.expander("Cara menggunakan aplikasi"):
        st.markdown(
            "1. **Data**: isi nama pewangi dan nilai untuk tiap kriteria (angka bulat minimal 1).\n"
            "2. **Bobot & Jenis Kriteria**: atur seberapa penting tiap kriteria (0 sampai 5) dan pilih jenisnya "
            "(Benefit: makin besar makin baik, Cost: makin kecil makin baik).\n"
            "3. **Perhitungan**: lihat nilai pangkat, vektor S, dan vektor V langkah demi langkah.\n"
            "4. **Hasil**: lihat pewangi terfavorit, peringkat lengkap, dan uji skenario.")
    st.info("Catatan: jurnal memakai skala nilai 1 sampai 3 tetapi tidak menjelaskan artinya. Aplikasi menerima angka bulat "
            "1 sampai 5, dan nilai harus minimal 1 karena WP memerlukan nilai positif.", icon="ℹ️")
    cfg = {"Pewangi": st.column_config.TextColumn("Pewangi", required=True, width="medium")}
    singkat = ["Aroma", "Kualitas", "Alkohol", "Stok", "Varian"]
    for j, k in enumerate(wp.KRITERIA):
        cfg[k] = st.column_config.NumberColumn(wp.KODE[j], help=k, min_value=1, max_value=5, step=1,
                                               format="%d", required=True, width="small")
    st.caption("Keterangan kolom: " + "; ".join(f"{kd} = {kr}" for kd, kr in zip(wp.KODE, wp.KRITERIA)) + ".")
    data = st.data_editor(st.session_state["data"], num_rows="dynamic", width="stretch", hide_index=True, key="editor", column_config=cfg)
    data = data.reset_index(drop=True)
    if st.button("Kembalikan data ke jurnal"):
        st.session_state["data"] = wp.DATA_JURNAL.copy()
        st.session_state.pop("editor", None)
        st.rerun()

# ------------------------------------------------------------ bobot & jenis
with tab_bobot:
    st.subheader("Bobot dan Jenis Kriteria")
    st.caption("Bobot menunjukkan tingkat kepentingan (0 = diabaikan, 5 = sangat penting). Bobot dinormalisasi otomatis "
               "sehingga totalnya 1. Jurnal menganggap seluruh kriteria sebagai benefit.")
    bobot, jenis = [], []
    for j, (kode, nama) in enumerate(zip(wp.KODE, wp.KRITERIA)):
        c1, c2 = st.columns([3, 2])
        bobot.append(c1.slider(f"{kode}: {nama}", 0, 5, key=f"bobot{j}", help="; ".join(f"{k} = {v}" for k, v in wp.SKALA_BOBOT.items())))
        jenis.append("cost" if c2.radio("Jenis", ["Benefit", "Cost"], key=f"jenis{j}", horizontal=True, label_visibility="visible") == "Cost" else "benefit")
    if "cost" in jenis:
        st.warning("Kriteria bertipe Cost dihitung dengan pangkat negatif (semakin kecil nilainya semakin baik).")
    if st.button("Kembalikan bobot dan jenis ke jurnal"):
        for j in range(5):
            st.session_state[f"bobot{j}"] = wp.BOBOT_JURNAL[j]
            st.session_state[f"jenis{j}"] = "Benefit"
        st.rerun()
    if sum(bobot) > 0:
        wn = [b / sum(bobot) for b in bobot]
        st.success(f"Total bobot: {sum(bobot)}. Bobot dinormalisasi otomatis sehingga totalnya 1,00.")
        st.dataframe(pd.DataFrame([wn], columns=wp.KODE, index=["Bobot ternormalisasi (W)"]).round(4), width="stretch")
    else:
        st.error("Total bobot masih 0. Naikkan bobot minimal satu kriteria.")

# ------------------------------------------------------------ validasi & hitung
galat = wp.validasi(data, bobot)
hit = None if galat else wp.hitung(data, bobot, jenis)
nama = [] if galat else data["Pewangi"].astype(str).str.strip().tolist()

with tab_hitung:
    if galat:
        for g in galat:
            st.error(g)
    else:
        st.subheader("1. Matriks Keputusan (X)")
        st.dataframe(pd.DataFrame(hit["x"], index=nama, columns=wp.KODE).astype(int), width="stretch")
        st.subheader("2. Bobot Ternormalisasi dan Pangkat")
        st.latex(r"W_j = \dfrac{w_j}{\sum w_j}, \qquad \text{pangkat} = +W_j \text{ (benefit)} \; / \; -W_j \text{ (cost)}")
        st.dataframe(pd.DataFrame([hit["wn"], hit["pangkat"]], columns=wp.KODE, index=["Bobot ternormalisasi (W)", "Pangkat"]).round(4), width="stretch")
        st.subheader("3. Nilai Pangkat dan Vektor S")
        st.latex(r"S_i = \prod_{j=1}^{n} x_{ij}^{\,\text{pangkat}_j}")
        tabel_s = pd.DataFrame(hit["f"], index=nama, columns=wp.KODE)
        tabel_s["Vektor S"] = hit["s"]
        st.dataframe(tabel_s.round(4).assign(**{"Vektor S": tabel_s["Vektor S"].round(6)}), width="stretch")
        st.caption(f"Jumlah seluruh S = {hit['s'].sum():.6f}")
        st.subheader("4. Vektor V")
        st.latex(r"V_i = \dfrac{S_i}{\sum_{k=1}^{m} S_k}")
        tabel_v = pd.DataFrame({"Vektor S": hit["s"], "Vektor V": hit["v"]}, index=nama)
        st.dataframe(tabel_v.round(6), width="stretch")
        st.caption(f"Jumlah seluruh V = {hit['v'].sum():.6f}")
        with st.expander("Contoh perhitungan satu pewangi"):
            pil = st.selectbox("Pilih pewangi", nama, key="contoh")
            i = nama.index(pil)
            faktor = " × ".join(f"{hit['x'][i, j]:g}^{hit['pangkat'][j]:.2f}" for j in range(5))
            nilai = " × ".join(f"{hit['f'][i, j]:.4f}" for j in range(5))
            st.markdown(f"**S** = {faktor}  \n= {nilai}  \n= **{hit['s'][i]:.6f}**  \n**V** = {hit['s'][i]:.6f} / {hit['s'].sum():.6f} = **{hit['v'][i]:.6f}**")

# ------------------------------------------------------------ hasil
with tab_hasil:
    if galat:
        for g in galat:
            st.error(g)
    else:
        h = hit["hasil"]
        puncak = h[h["Peringkat"] == 1]
        seri = len(puncak) > 1
        judul = "SERI DI PERINGKAT PERTAMA" if seri else "PEWANGI SETRIKA TERFAVORIT"
        st.markdown(f'<div class="rekom{" seri" if seri else ""}"><small>{judul}</small><h2>{" & ".join(puncak["Pewangi"])}</h2>'
                    f'<span>Nilai vektor V: {puncak.iloc[0]["Nilai (V)"]:.4f} (Peringkat 1)</span></div>', unsafe_allow_html=True)
        if seri:
            st.warning("Ada lebih dari satu pewangi dengan nilai tertinggi yang sama. Gunakan pertimbangan lain sebelum memutuskan.")
        dom = wp.dominan(data, jenis)
        if dom and not seri:
            st.info(f"**{dom[0]}** memiliki nilai terbaik di semua kriteria, sehingga pemenangnya tidak berubah berapa pun "
                    "bobot yang dipilih. Bobot hanya memengaruhi urutan pewangi lainnya.", icon="💡")
        st.subheader("Tabel Peringkat")
        st.dataframe(h, width="stretch", hide_index=True,
                     column_config={"Vektor S": st.column_config.NumberColumn(format="%.6f"),
                                    "Nilai (V)": st.column_config.NumberColumn(format="%.4f")})
        st.download_button("Unduh hasil (CSV)", h.to_csv(index=False).encode("utf-8"), file_name="hasil_pewangi_wp.csv", mime="text/csv")
        st.subheader("Grafik Perbandingan Nilai V")
        st.bar_chart(h, x="Pewangi", y="Nilai (V)", sort="-Nilai (V)")
        st.subheader("Uji Skenario")
        st.caption("Memeriksa apakah pemenang berubah jika semua bobot disamakan atau jika jenis satu kriteria dibalik "
                   "(benefit menjadi cost atau sebaliknya).")
        sk = wp.skenario(data, bobot, jenis)
        st.dataframe(sk, width="stretch", hide_index=True, column_config={"Nilai (V)": st.column_config.NumberColumn(format="%.4f")})
        if (sk["Sama dengan pengaturan saat ini"] == "Tidak").any():
            st.warning("Pemenang berubah pada sebagian skenario. Pastikan jenis kriteria dan bobot sudah sesuai dengan kebutuhan "
                       "sebelum memakai rekomendasi ini.")
        else:
            st.success("Pemenang sama pada semua skenario yang diuji.")
        st.caption("Aplikasi ini membantu keputusan; keputusan akhir tetap di tangan pemilik laundry.")
