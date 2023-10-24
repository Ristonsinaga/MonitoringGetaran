from supabase import create_client
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import time
import numpy as np
from scipy.fft import fft, fftshift
import plotly.express as px


# Ganti dengan informasi Supabase Anda
API_URL = 'https://tytohrcddnmmkqazxhuc.supabase.co'
API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5dG9ocmNkZG5tbWtxYXp4aHVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTczODAzNDMsImV4cCI6MjAxMjk1NjM0M30.v-Hag5MMPDDRiHS3Z--WbUfMo_aNIFooN1vja5CaI7k'  # Ganti dengan kunci API Anda

# Inisialisasi klien Supabase
supabase = create_client(API_URL, API_KEY)

import streamlit as st

# Inisialisasi halaman Streamlit
st.set_page_config(page_title="Dashboard", layout='wide', initial_sidebar_state='collapsed')


# Buat tampilan judul
st.markdown(
    """
    <style>
    .blue-rectangle {
    background-color: maroon;
    padding: 10px 170px;
    border-radius: 2px;
    display: inline-block;
    }
    </style>
    <div style="text-align: center; font-family: Arial Black; font-size: 50px;">
    <div class="blue-rectangle">SISTEM INFORMASI MONITORING GETARAN MESIN</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Tambahkan teks tentang kegunaan web
st.write("Selamat datang di Sistem Informasi Monitoring Getaran Mesin. Website ini dirancang untuk memantau dan menganalisis data getaran mesin. Anda dapat melihat data tachometer termasuk akselerasi dalam bentuk grafik Time Domain, dan analisis Domain Frekuensi. Data diambil sebanyak 2000 data, dengan delay 2 ms.")

# Buat tempat kosong untuk grafik
row1, row2, row3 = st.columns(3)

# Spedometer
spedometer_chart = row1.empty()
# Grafik RPM
rpm_chart = row2.empty()
# Akselerometer
acceleration_chart = row3.empty()

row4 = st.columns(1)
table_chart = row4[0].empty()


while True:
    supabaseList = supabase.table('RPM').select('*').execute().data

    df = pd.DataFrame()
    for row in supabaseList:
        row["created_at"] = row["created_at"].split(".")[0]
        row["time"] = row["created_at"].split("T")[1]
        row["date"] = row["created_at"].split("T")[0]
        row["DateTime"] = row["id"]  # ganti dengan created_at atau kolom waktu yang sesuai
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    # Mengurutkan dataframe berdasarkan kolom "DateTime"
    df = df.sort_values(by="DateTime")

    # Buat grafik RPM dengan Plotly Express
    rpm_fig = px.line(df, x="DateTime", y="rpm", title="Grafik RPM")
    rpm_fig.update_xaxes(title_text="Waktu")
    rpm_fig.update_yaxes(title_text="RPM")

    # Buat tampilan spidometer dengan ukuran kustom
    spedometer_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=df["rpm"].iloc[-1],  # Nilai terbaru dari RPM
        title={'text': "Kecepatan (RPM)"},
        gauge={'axis': {'range': [min(df["rpm"]), max(df["rpm"])]},
               'steps': [{'range': [min(df["rpm"]), max(df["rpm"]) / 2], 'color': "lightgray"},
                         {'range': [max(df["rpm"]) / 2, max(df["rpm"])], 'color': "gray"}],
               'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': df["rpm"].iloc[-1]}}))

    # Atur ukuran kustom untuk tampilan spidometer
    spedometer_fig.update_layout(height=400, width=350)  # Sesuaikan tinggi dan lebar sesuai kebutuhan

    # Ambil data akselerasi_x, akselerasi_y, dan akselerasi_z
    acceleration_x = df["acceleration_x"]
    acceleration_y = df["acceleration_y"]
    acceleration_z = df["acceleration_z"]

    # Buat plotly figure untuk grafik akselerasi
    acceleration_fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.05)

    acceleration_fig.add_trace(go.Scatter(x=df["DateTime"], y=acceleration_x, name="Akselerasi X", mode='lines', line=dict(color='blue')))
    acceleration_fig.add_trace(go.Scatter(x=df["DateTime"], y=acceleration_y, name="Akselerasi Y", mode='lines', line=dict(color='green')))
    acceleration_fig.add_trace(go.Scatter(x=df["DateTime"], y=acceleration_z, name="Akselerasi Z", mode='lines', line=dict(color='red')))

    # Atur tampilan grafik akselerasi
    acceleration_fig.update_layout(
        title="Grafik Akselerasi",
        xaxis_title="Waktu",
        yaxis_title="Nilai Akselerasi",
        showlegend=True
    )

    # Tampilkan grafik RPM, spedometer, dan akselerometer di tampilan Streamlit
    rpm_chart.plotly_chart(rpm_fig, use_container_width=True)
    spedometer_chart.plotly_chart(spedometer_fig, use_container_width=True)
    acceleration_chart.plotly_chart(acceleration_fig, use_container_width=True)

    # Hitung nilai puncak dari ketiga sumbu akselerasi
    peak_x = df["acceleration_x"].max()
    peak_y = df["acceleration_y"].max()
    peak_z = df["acceleration_z"].max()


    # Hitung nilai peak, RMS, Average, dan Peak to Peak untuk ketiga kolom akselerasi
    peak_x = df["acceleration_x"].max()
    rms_x = 0.707 * peak_x
    average_x = 0.637 * peak_x
    peak_to_peak_x = df["acceleration_x"].max() - df["acceleration_x"].min()

    peak_y = df["acceleration_y"].max()
    rms_y = 0.707 * peak_y
    average_y = 0.637 * peak_y
    peak_to_peak_y = df["acceleration_y"].max() - df["acceleration_y"].min()

    peak_z = df["acceleration_z"].max()
    rms_z = 0.707 * peak_z
    average_z = 0.637 * peak_z
    peak_to_peak_z = df["acceleration_z"].max() - df["acceleration_z"].min()

    # Hitung nilai Hertz (Hz) dari RPM
    rpm = df["rpm"].iloc[-1]  # Ambil nilai RPM terbaru
    hz = rpm / 60
    hz2 = 2 * hz
    hz3 = 3 * hz
    hz4 = 4 * hz

    # Buat DataFrame untuk tabel peak, peak to peak, RMS, dan average
    peak_df = pd.DataFrame({
        "Parameter": ["Axial X", "Axial Y", "Radial Z", "Frekuensi"],
        "Peak": [f"{peak_x} (mm/s²)", f"{peak_y} (mm/s²)", f"{peak_z} (mm/s²)", f"{hz} Hz"],
        "Peak to Peak": [f"{peak_to_peak_x} (mm/s²)", f"{peak_to_peak_y} (mm/s²)", f"{peak_to_peak_z} (mm/s²)", f"{hz2} Hz"],
        "RMS": [f"{rms_x} (mm/s²)", f"{rms_y} (mm/s²)", f"{rms_z} (mm/s²)", f"{hz3} Hz"],
        "Average": [f"{average_x} (mm/s²)", f"{average_y} (mm/s²)", f"{average_z} (mm/s²)", f"{hz4} Hz"]
    })

    # Menambahkan kolom Status
    threshold = 2 # Nilai ambang batas
    peak_df["Status"] = ["Bahaya" if peak_x > threshold else "Aman",
                         "Bahaya" if peak_y > threshold else "Aman",
                         "Bahaya" if peak_z > threshold else "Aman",
                         "Bahaya" if hz > threshold else "Aman"]


    # Tampilkan hasil perhitungan dalam tabel
    table_chart.table(peak_df)


    # Tampilkan tabel peak dan Hz
    table_chart.table(peak_df)
