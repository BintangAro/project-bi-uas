from django.shortcuts import render
import pandas as pd

def dashboard_utama(request):
    # Load dan normalisasi header kolom
    df_penjualan = pd.read_csv("biapp/data/dwh_penjualan_detailed.csv")
    df_revenue = pd.read_csv("biapp/data/dwh_revenue_detailed.csv")
    df_kontribusi = pd.read_csv("biapp/data/dwh_kontribusi_detailed.csv")

    for df in [df_penjualan, df_revenue, df_kontribusi]:
        df.columns = df.columns.str.strip().str.lower()  # Normalisasi nama kolom

    # Cek apakah kolom ada
    if 'provinsi' not in df_penjualan.columns or 'tahun' not in df_penjualan.columns:
        return render(request, "dashboard.html", {
            "error": "Kolom 'provinsi' atau 'tahun' tidak ditemukan di data penjualan."
        })

    # Siapkan opsi filter
    region_options = sorted(df_penjualan['provinsi'].dropna().unique())
    tahun_options = sorted(df_penjualan['tahun'].dropna().unique())

    selected_region = request.GET.get('region', 'Semua')
    selected_year = request.GET.get('tahun', 'Semua')

    # Fungsi filter
    def apply_filter(df):
        if 'provinsi' in df.columns and selected_region != 'Semua':
            df = df[df['provinsi'] == selected_region]
        if 'tahun' in df.columns and selected_year != 'Semua':
            df = df[df['tahun'] == int(selected_year)]
        return df

    # Terapkan filter ke semua dataframe
    df_penjualan_filtered = apply_filter(df_penjualan)
    df_revenue_filtered = apply_filter(df_revenue)
    df_kontribusi_filtered = apply_filter(df_kontribusi)

    # Siapkan data untuk chart
    chart_penjualan = {
        "labels": list(df_penjualan_filtered['nama_produk']),
        "actual": list(df_penjualan_filtered['qty']),
    }

    chart_revenue = {
        "labels": list(df_revenue_filtered['nama_produk']),
        "revenue": list(df_revenue_filtered['revenue_bersih']),
    }

    chart_kontribusi = {
        "labels": list(df_kontribusi_filtered['nama_channel']),
        "qty": list(df_kontribusi_filtered['total_qty']),
    }

    return render(request, "dashboard.html", {
        "region_options": ['Semua'] + region_options,
        "tahun_options": ['Semua'] + [str(t) for t in tahun_options],
        "selected_region": selected_region,
        "selected_year": selected_year,
        "chart_penjualan": chart_penjualan,
        "chart_revenue": chart_revenue,
        "chart_kontribusi": chart_kontribusi,
    })
