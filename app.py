import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from st_supabase_connection import SupabaseConnection

st.set_page_config(page_title="Dashboard Pro Data & AI", layout="wide")
st.title("🚀 Dashboard Teknologi Tinggi: AI, Data & Database Cloud")

# =========================================================================
# POIN B: MENYALAKAN KONEKSI DATABASE CLOUD (SUPABASE)
# =========================================================================
# Mencoba mendeteksi apakah kredensial Secrets di Streamlit Cloud sudah aktif
try:
    conn = st.connection("supabase", type=SupabaseConnection)
except Exception:
    conn = None

# =========================================================================
# MANAGEMENT DATA SINKRONISASI
# =========================================================================
st.sidebar.header("📁 Manajemen Data")
berkas_diunggah = st.sidebar.file_uploader("Unggah Berkas Laporan Anda (CSV atau Excel)", type=["csv", "xlsx"])

if berkas_diunggah is not None:
    try:
        if berkas_diunggah.name.endswith(".csv"):
            tabel_data = pd.read_csv(berkas_diunggah)
        else:
            tabel_data = pd.read_excel(berkas_diunggah)
        st.sidebar.success("Berhasil memuat berkas luar!")
    except Exception as e:
        st.sidebar.error(f"Gagal membaca berkas: {e}")
        st.stop()
else:
    baris_default = [
        ("Arut Selatan", 15000, 16200),
        ("Kumai", 18500, 17900),
        ("Pangkalan Lada", 22000, 23100),
        ("Pangkalan Banteng", 25500, 24000)
    ]
    tabel_data = pd.DataFrame(baris_default, columns=["Kecamatan", "Target_Capaian", "Realisasi"])
    st.sidebar.info("Menggunakan data simulasi internal.")

tabel_data = tabel_data.drop_duplicates()

# Tampilan Layout Dashboard
kolom1, kolom2 = st.columns(2)
with kolom1:
    st.subheader("📋 Lembar Tabel Data")
    st.dataframe(tabel_data, use_container_width=True)

with kolom2:
    st.subheader("📊 Grafik Realisasi")
    if "Kecamatan" in tabel_data.columns and "Realisasi" in tabel_data.columns:
        st.bar_chart(tabel_data, x="Kecamatan", y="Realisasi")

# =========================================================================
# TRAINING MODEL AI & SIMULASI PREDIKSI + REAL-TIME SAVE TO DB
# =========================================================================
st.markdown("---")
st.subheader("🤖 Generator Prediksi Otomatis (Machine Learning)")

if "Target_Capaian" in tabel_data.columns and "Realisasi" in tabel_data.columns:
    X = tabel_data[["Target_Capaian"]]
    y = tabel_data["Realisasi"]
    model_ai = LinearRegression()
    model_ai.fit(X, y)
    
    input_target = st.number_input("Masukkan Target Capaian Baru:", min_value=1000, value=30000, step=1000)
    
    if st.button("Hitung Estimasi & Simpan ke Server Cloud"):
        data_baru = pd.DataFrame({"Target_Capaian": [input_target]})
        hasil_prediksi = model_ai.predict(data_baru)
        
        st.success(f"🔮 Prediksi Realisasi AI: **{hasil_prediksi:,.2f}**")
        
        # Eksekusi penyimpanan data ke database Supabase secara real-time
        if conn is not None:
            try:
                log_data = {"target_input": float(input_target), "hasil_prediksi": float(hasil_prediksi)}
                conn.table("riwayat_prediksi").insert(log_data).execute()
                st.info("💾 Data log prediksi berhasil dikirim dan disimpan secara permanen di Database Cloud!")
            except Exception as db_err:
                st.warning(f"Koneksi terdeteksi, namun gagal menyimpan: {db_err}. Pastikan Anda sudah menjalankan query pembentukan tabel 'riwayat_prediksi' di SQL Editor Supabase.")
        else:
            st.warning("Aplikasi berjalan offline. Kredensial rahasia database (Secrets) di Streamlit Cloud belum terpasang.")
else:
    st.error("Model AI tidak bisa dilatih karena kolom 'Target_Capaian' atau 'Realisasi' tidak ada.")
