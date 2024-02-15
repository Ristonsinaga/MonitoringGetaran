from supabase import create_client
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft, fftshift
import altair as alt
import plotly.express as px
import numpy as np
import plotly.express as px



# Ganti dengan informasi Supabase Anda
API_URL = 'https://tytohrcddnmmkqazxhuc.supabase.co'
API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5dG9ocmNkZG5tbWtxYXp4aHVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTczODAzNDMsImV4cCI6MjAxMjk1NjM0M30.v-Hag5MMPDDRiHS3Z--WbUfMo_aNIFooN1vja5CaI7k'  # Ganti dengan kunci API Anda

# Inisialisasi klien Supabase
supabase = create_client(API_URL, API_KEY)

import streamlit as st

# Inisialisasi halaman Streamlit
st.set_page_config(page_title="Dashboard", layout='wide', initial_sidebar_state='collapsed')

# ...

# Buat tampilan judul dengan latar belakang putih
st.markdown(
    """
    <style>
    body {
        background-color: white;
    }
    .blue-rectangle {
        background-color: maroon;
        padding: 10px 170px;
        border-radius: 2px;
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
st.write("Selamat datang di Sistem Informasi Monitoring Getaran Mesin. Website ini dirancang untuk memantau dan menganalisis data getaran mesin. Anda dapat melihat data tachometer termasuk akselerasi dalam bentuk grafik Time Domain, dan analisis Domain Frekuensi. Data diambil sebanyak 2100 data, dengan delay 2 ms.")


# Tambahkan tombol "Update Data"
if st.button("Update Data"):
    supabaseList = supabase.table('maintable').select('*').execute().data

    df = pd.DataFrame()
    for row in supabaseList:
        row["created_at"] = row["created_at"].split(".")[0]
        row["time"] = row["created_at"].split("T")[1]
        row["date"] = row["created_at"].split("T")[0]
        row["DateTime"] = row["created_at"]
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    # Pilih data terakhir secara otomatis
    selected_id = df['created_at'].max()

    # Informasikan pengguna bahwa data telah diperbarui dan data terakhir telah dipilih
    st.success("Data telah diperbarui!")


while True:
    supabaseList = supabase.table('maintable').select('*').execute().data

    df = pd.DataFrame()
    for row in supabaseList:
        row["created_at"] = row["created_at"].split(".")[0]
        row["time"] = row["created_at"].split("T")[1]
        row["date"] = row["created_at"].split("T")[0]
        row["DateTime"] = row["id"]
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    # Tambahkan elemen input untuk memilih ID
    selected_id = st.selectbox('Pilih Waktu', df['created_at'].unique())


    # Ambil data acceleration_x, acceleration_y, dan acceleration_z berdasarkan ID yang dipilih
    selected_data_x = df[df['created_at'] == selected_id]['acceleration_x'].values[0]
    selected_data_y = df[df['created_at'] == selected_id]['acceleration_y'].values[0]
    selected_data_z = df[df['created_at'] == selected_id]['acceleration_z'].values[0]

    # Hapus karakter '[' dan ']' dari string
    selected_data_x = selected_data_x.strip('[]')
    selected_data_y = selected_data_y.strip('[]')
    selected_data_z = selected_data_z.strip('[]')

    # Ganti koma (',') dengan titik desimal ('.') dan pisahkan string menjadi daftar nilai numerik
    selected_data_values_x = [float(val.replace(',', '.')) for val in selected_data_x.split(',')]
    selected_data_values_y = [float(val.replace(',', '.')) for val in selected_data_y.split(',')]
    selected_data_values_z = [float(val.replace(',', '.')) for val in selected_data_z.split(',')]


    # Menghitung offset untuk sumbu Z
    offset_x = 0.02  # Nilai yang ingin dijadikan nol
    selected_data_values_x = [val - offset_x for val in selected_data_values_x]

    offset_y = 0.01  # Nilai yang ingin dijadikan nol
    selected_data_values_y = [val - offset_y for val in selected_data_values_y]

    # Menghitung offset untuk sumbu Z
    offset_z = 21.48  # Nilai yang ingin dijadikan nol
    selected_data_values_z = [(val *1638.4)/819.2 - offset_z for val in selected_data_values_z]



    # Hitung Peak, RMS, Average, dan Peak to Peak untuk ketiga kolom akselerasi
    peak_x = np.max(np.abs(selected_data_values_x))
    rms_x = 0.707 * peak_x
    average_x = 0.637 * peak_x
    peak_to_peak_x = np.max(selected_data_values_x) - np.min(selected_data_values_x)

    peak_y = np.max(np.abs(selected_data_values_y))
    rms_y = 0.707 * peak_y
    average_y = 0.637 * peak_y
    peak_to_peak_y = np.max(selected_data_values_y) - np.min(selected_data_values_y)

    peak_z = np.max(np.abs(selected_data_values_z))
    rms_z = 0.707 * peak_z
    average_z = 0.637 * peak_z
    peak_to_peak_z = np.max(selected_data_values_z) - np.min(selected_data_values_z)

    # Tentukan warna berdasarkan nilai puncak
    def get_warning_info(peak):
        if peak > 1:
            return ("red", "Bahaya 🚨🚨🚨")
        else:
            return ("green", "Aman")

    # Data untuk tabel karakteristik misalignment
    data_misalignment = {
        'Misalignment': ['Pararel', 'Angular'],
        'Karakteristik': [
            'Spektrum menunjukkan getaran radial yang tinggi pada 2X dan 1X yang lebih rendah dengan perbedaan fasa 180° melintasi kopling dalam arah radial.',
            'Sinyal getaran 1X dan 2X yang dominan pada arah aksial',
        ]
    }

    # Convert data karakteristik misalignment ke DataFrame
    df_misalignment = pd.DataFrame(data_misalignment)

    # Data untuk tabel akselerasi
    data_acceleration = {
        'Arah': ['Axial', 'Radial Y', 'Radial Z'],
        'Peak': [peak_x, peak_y, peak_z],
        'RMS': [rms_x, rms_y, rms_z],
        'Average': [average_x, average_y, average_z],
        'Peak to Peak': [peak_to_peak_x, peak_to_peak_y, peak_to_peak_z],
        'Kondisi': [
            f'<span style="color: {get_warning_info(peak_x)[0]}">{get_warning_info(peak_x)[1]}</span>',
            f'<span style="color: {get_warning_info(peak_y)[0]}">{get_warning_info(peak_y)[1]}</span>',
            f'<span style="color: {get_warning_info(peak_z)[0]}">{get_warning_info(peak_z)[1]}</span>'
        ]
    }

    # Convert data akselerasi ke DataFrame
    df_acceleration = pd.DataFrame(data_acceleration)

    # CSS untuk membuat semua isi tabel menjadi rata kiri
    css = """
    th, td {
        text-align: left !important;
    }
    """
    # Render the HTML properly
    st.write(f'<style>{css}</style>', unsafe_allow_html=True)

    # Layout kolom Streamlit
    col1, col2 = st.columns(2)

    # Tampilkan tabel karakteristik misalignment di kolom pertama (kanan)
    with col1:
        st.write("Tabel Karakteristik Misalignment:")
        st.write(df_misalignment.to_html(escape=False), unsafe_allow_html=True)

    # Tampilkan tabel akselerasi di kolom kedua (kiri)
    with col2:
        st.write("Tabel Akselerasi:")
        st.write(df_acceleration.to_html(escape=False), unsafe_allow_html=True)

    # Buat tempat kosong awal untuk grafik
    spedometer_chart = st.empty()
    row1, row2, row3 = st.columns([3, 3, 3])
    acceleration_x_chart = row1.empty()
    acceleration_y_chart = row2.empty()
    acceleration_z_chart = row3.empty()

    # ... (kode sebelumnya)
    row1, row2, row3 = st.columns([3, 3, 3])
    # Inisialisasi objek chart FFT untuk X, Y, dan Z
    acceleration_fft_x_chart = row1.empty()
    acceleration_fft_y_chart = row2.empty()
    acceleration_fft_z_chart = row3.empty()


    # Waktu antara setiap data dalam milidetik (ms)
    time_step_ms = 3

    # Jumlah data
    num_data_points = 1500

    # Waktu total yang dicakup dalam data (detik)
    total_time_seconds = (time_step_ms * num_data_points) / 1000  # Konversi dari ms ke detik

    # Data waktu (dalam detik)
    time_values = [i * (time_step_ms / 1000) for i in range(num_data_points)]

    # Membuat DataFrame untuk akselerasi X, Y, dan Z
    data = {
        'Time (s)': time_values,
        'Akselerasi X': selected_data_values_x,
        'Akselerasi Y': selected_data_values_y,
        'Akselerasi Z': selected_data_values_z
    }
    df = pd.DataFrame(data)

    # Membuat grafik akselerasi X, Y, dan Z dalam domain waktu dengan Plotly Express
    fig_x = px.line(df, x='Time (s)', y='Akselerasi X', title=f'Time Domain {selected_id}', width=600, height=400)
    fig_x.update_traces(line=dict(color='blue', width=0.6), name='Akselerasi X')
    fig_x.update_xaxes(title_text='Waktu (detik)')
    fig_x.update_yaxes(title_text='Amplitudo (mm/s²)')


    fig_y = px.line(df, x='Time (s)', y='Akselerasi Y', title=f'Time Domain {selected_id}', width=600, height=400)
    fig_y.update_traces(line=dict(color='blue', width=0.6), name='Akselerasi Y')
    fig_y.update_xaxes(title_text='Waktu (detik)')
    fig_y.update_yaxes(title_text='Amplitudo (mm/s²)')

    # Konversi data ke DataFrame
    df_acceleration_z = pd.DataFrame({'Time (s)': time_values, 'Akselerasi Z': selected_data_values_z})

    # Konversi data ke DataFrame
    df_acceleration_x = pd.DataFrame({'Time (s)': time_values, 'Akselerasi X': selected_data_values_x})
    df_acceleration_y = pd.DataFrame({'Time (s)': time_values, 'Akselerasi Y': selected_data_values_y})
    df_acceleration_z = pd.DataFrame({'Time (s)': time_values, 'Akselerasi Z': selected_data_values_z})

    # Layout kolom Streamlit
    col1, col2, col3 = st.columns(3)

    # Menampilkan tabel akselerasi X di kolom pertama (kiri)
    with col1:
        st.write("Tabel Akselerasi X")
        st.dataframe(df_acceleration_x)

    # Menampilkan tabel akselerasi Y di kolom kedua (tengah)
    with col2:
        st.write("Tabel Akselerasi Y")
        st.dataframe(df_acceleration_y)

    # Menampilkan tabel akselerasi Z di kolom ketiga (kanan)
    with col3:
        st.write("Tabel Akselerasi Z")
        st.dataframe(df_acceleration_z)


    fig_z = px.line(df, x='Time (s)', y='Akselerasi Z', title=f'Time Domain {selected_id}', width=600, height=400)
    fig_z.update_traces(line=dict(color='blue', width=0.6), name='Akselerasi Z')
    fig_z.update_xaxes(title_text='Waktu (detik)')
    fig_z.update_yaxes(title_text='Amplitudo (mm/s²)')

    # Tampilkan grafik akselerasi X, Y, dan Z dengan Plotly Express
    acceleration_x_chart.plotly_chart(fig_x)
    acceleration_y_chart.plotly_chart(fig_y)
    acceleration_z_chart.plotly_chart(fig_z)

    # Hitung FFT untuk ketiga kolom akselerasi dibagi 1000  bisa juga dibagi ini: 1019.71687
    fft_x = fft(selected_data_values_x)/1000
    fft_y = fft(selected_data_values_y)/1000
    fft_z = fft(selected_data_values_z)/1000


    # Atur sumbu frekuensi untuk FFT
    N = len(selected_data_values_z)
    freq = np.fft.fftfreq(N, 4.5 / 1500)  # 200 adalah frekuensi sampel, ganti sesuai kebutuhan

    # Ambil hanya komponen frekuensi positif
    positive_freq_indices = np.where((freq >= 0)) 
    freq_positive = freq[positive_freq_indices]

    # Buat tiga gambar terpisah untuk FFT akselerasi X, Y, dan Z menggunakan Plotly Express
    fig_x = px.line(x=freq_positive, y=np.abs(fft_x[positive_freq_indices]), title=f'Domain Frekuensi X - {selected_id}')
    fig_x.update_xaxes(title_text='Frekuensi (Hz)')
    fig_x.update_yaxes(title_text='Amplitudo (mm/s2)')
    fig_x.update_traces(line=dict(color='blue', width=0.5), name='FFT acceleration_x')
    fig_x.update_layout(width=600, height=400)
    acceleration_fft_x_chart.plotly_chart(fig_x)

    fig_y = px.line(x=freq_positive, y=np.abs(fft_y[positive_freq_indices]), title=f'Domain Frekuensi Y - {selected_id}')
    fig_y.update_xaxes(title_text='Frekuensi (Hz)')
    fig_y.update_yaxes(title_text='Amplitudo (mm/s2)')
    fig_y.update_traces(line=dict(color='blue', width=0.5), name='FFT acceleration_y')
    fig_y.update_layout(width=600, height=400)
    acceleration_fft_y_chart.plotly_chart(fig_y)


    fig_z = px.line(x=freq_positive, y=np.abs(fft_z[positive_freq_indices]), title=f'Domain Frekuensi Z - {selected_id}')
    fig_z.update_xaxes(title_text='Frekuensi (Hz)')
    fig_z.update_yaxes(title_text='Amplitudo (mm/s2)')
    fig_z.update_traces(line=dict(color='blue', width=0.5), name='FFT acceleration_z')
    fig_z.update_layout(width=600, height=400)
    acceleration_fft_z_chart.plotly_chart(fig_z)



    
