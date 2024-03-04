from supabase import create_client
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time



# Ganti dengan informasi Supabase Anda
API_URL = 'https://tytohrcddnmmkqazxhuc.supabase.co'
API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5dG9ocmNkZG5tbWtxYXp4aHVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTczODAzNDMsImV4cCI6MjAxMjk1NjM0M30.v-Hag5MMPDDRiHS3Z--WbUfMo_aNIFooN1vja5CaI7k'  # Ganti dengan kunci API Anda

# Inisialisasi klien Supabase
supabase = create_client(API_URL, API_KEY)

# Inisialisasi halaman Streamlit
st.set_page_config(page_title="Dashboard", layout='wide', initial_sidebar_state='collapsed')

st.markdown(
    """
    <style>
    body {
        background-color: white;
    }
    .blue-rectangle {
        background-color: maroon;
        padding: 10px 170px;
        border-radius: 5px;
        display: inline-block;
    }
    .white-text {
        color: white;  /* Mengatur warna teks menjadi putih */
    }
    </style>
    <div style="text-align: center; font-family: Arial Black; font-size: 48px;">
    <div class="blue-rectangle white-text">SISTEM INFORMASI MONITORING GETARAN MESIN</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Tambahkan teks tentang kegunaan web
st.write("Selamat datang di Sistem Informasi Monitoring Getaran Mesin. Website ini dirancang untuk memantau dan menganalisis data getaran mesin. Anda dapat melihat data tachometer termasuk akselerasi dalam bentuk grafik Time Domain, dan analisis Domain Frekuensi. Data diambil sebanyak 1500 data, dengan delay 2 ms.")

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
        # Parse "created_at" with fractional seconds
        created_at_datetime = datetime.strptime(row["created_at"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
        
        # Add 7 hours to the timestamp
        adjusted_datetime = created_at_datetime + timedelta(hours=7)

        # Update the row with adjusted date and time
        row["created_at"] = adjusted_datetime.strftime("%Y-%m-%dT%H:%M:%S")
        row["time"] = adjusted_datetime.strftime("%H:%M:%S")
        row["date"] = adjusted_datetime.strftime("%Y-%m-%d")
        row["DateTime"] = adjusted_datetime.strftime("%Y-%m-%dT%H:%M:%S")  # You can change this line accordingly

        # Concatenate the row to the DataFrame
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    # Mengurutkan dataframe berdasarkan kolom "DateTime"
    df = df.sort_values(by="DateTime")

    # Buat grafik RPM dengan Plotly Express
    rpm_fig = px.line(df, x="DateTime", y="rpm", title="Grafik RPM")
    rpm_fig.update_xaxes(title_text="Waktu")
    rpm_fig.update_yaxes(title_text="RPM")

    # Tambahkan trace untuk menampilkan timestamp di bawah grafik RPM
    rpm_fig.add_trace(go.Scatter(x=df["DateTime"], y=[0] * len(df), mode='markers+text',
                                text=df["time"], textposition="bottom center", marker=dict(size=0),
                                showlegend=False))

    # Buat tampilan spidometer dengan ukuran kustom
    spedometer_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=df["rpm"].iloc[-1],  # Nilai terbaru dari RPM
        title={'text': f"Kecepatan (RPM) - {df['time'].iloc[-1]}"},  # Add timestamp to the title
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

    # Menghitung offset untuk sumbu x
    offset_x = 0.04  # Nilai yang ingin dijadikan nol
    acceleration_x = [val - offset_x for val in acceleration_x]

    # Menghitung offset untuk sumbu x
    offset_y = 0.04  # Nilai yang ingin dijadikan nol
    acceleration_y = [val - offset_x for val in acceleration_y]

    # Menghitung offset untuk sumbu Z
    offset_z = 0.97  # Nilai yang ingin dijadikan nol
    acceleration_z = [val - offset_z for val in acceleration_z]

    # Buat plotly figure untuk grafik akselerasi
    acceleration_fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.05)

    acceleration_fig.add_trace(go.Scatter(x=df["DateTime"], y=acceleration_x, name="Akselerasi X", mode='lines', line=dict(color='blue')))
    acceleration_fig.add_trace(go.Scatter(x=df["DateTime"], y=acceleration_y, name="Akselerasi Y", mode='lines', line=dict(color='green')))
    acceleration_fig.add_trace(go.Scatter(x=df["DateTime"], y=acceleration_z, name="Akselerasi Z", mode='lines', line=dict(color='red')))

    # Atur tampilan grafik akselerasi
    acceleration_fig.update_layout(
        title="Grafik Kecepatan Getaran (Vrms)",
        xaxis_title="Waktu",
        yaxis_title="Vrms (mm/s)",
        showlegend=True
    )

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
    threshold = 2  # Nilai ambang batas
    peak_df["Status"] = ["Bahaya" if peak_x > threshold else "Aman",
                         "Bahaya" if peak_y > threshold else "Aman",
                         "Bahaya" if peak_z > threshold else "Aman",
                         "Bahaya" if hz > threshold else "Aman"]

    # Tampilkan grafik RPM, spedometer, dan akselerometer di tampilan Streamlit
    rpm_chart.plotly_chart(rpm_fig, use_container_width=True)
    spedometer_chart.plotly_chart(spedometer_fig, use_container_width=True)
    acceleration_chart.plotly_chart(acceleration_fig, use_container_width=True)

    # Tampilkan hasil perhitungan dalam tabel
    table_chart.table(peak_df)

    # Tunggu 5 detik sebelum memperbarui data (sesuaikan dengan kebutuhan)
    time.sleep(5)
