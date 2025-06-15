from django.shortcuts import render
import pandas as pd

def dashboard_utama(request):
    # Load data
    df_penjualan = pd.read_csv("/home/arouser/project-bi-uas/airflow_etl/data_output/dwh_penjualan_detailed.csv")
    df_revenue = pd.read_csv("/home/arouser/project-bi-uas/airflow_etl/data_output/dwh_model5g_detailed.csv")
    df_kontribusi = pd.read_csv("/home/arouser/project-bi-uas/airflow_etl/data_output/dwh_kontribusi_detailed.csv")

    # Daftar opsi filter
    region_options = sorted(df_penjualan['provinsi'].dropna().unique())
    tahun_options = sorted(df_penjualan['tahun'].dropna().unique())

    # Ambil filter dari parameter GET
    selected_region = request.GET.get('region', 'Semua')
    selected_year = request.GET.get('tahun', 'Semua')

    # Fungsi filter
    def apply_filter(df):
        if selected_region != 'Semua':
            df = df[df['provinsi'] == selected_region]
        if selected_year != 'Semua':
            df = df[df['tahun'] == int(selected_year)]
        return df

    # Filter data
    df_penjualan_filtered = apply_filter(df_penjualan)
    df_revenue_filtered = apply_filter(df_revenue)
    df_kontribusi_filtered = apply_filter(df_kontribusi)

    # === Grafik Penjualan (Star Schema 1) ===
    chart_penjualan = {
        "labels": list(df_penjualan_filtered['nama_produk']),
        "actual": list(df_penjualan_filtered['qty']),
    }

    # === Grafik Revenue Produk 5G (Star Schema 2) ===
    df_revenue_5g = df_revenue_filtered[df_revenue_filtered['fitur_5G'] == True]
    chart_revenue = {
        "labels": list(df_revenue_5g['nama_produk']),
        "revenue": list(df_revenue_5g['revenue_bersih']),
    }

    # === Grafik Kontribusi Wilayah (Star Schema 3) ===
    df_kontribusi_wilayah = df_kontribusi_filtered.groupby("provinsi")["total_qty"].sum().reset_index()
    chart_kontribusi = {
        "labels": list(df_kontribusi_wilayah["provinsi"]),
        "qty": list(df_kontribusi_wilayah["total_qty"]),
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
