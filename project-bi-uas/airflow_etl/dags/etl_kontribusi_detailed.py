from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os

# Lokasi file input dan output
FACT_KONTRIBUSI = "/home/arouser/project-bi-uas/airflow_etl/data_input/fact/fact_sales_schema3.csv"
DIM_PRODUCT = "/home/arouser/project-bi-uas/airflow_etl/data_input/dim/dim_product.csv"
DIM_REGION = "/home/arouser/project-bi-uas/airflow_etl/data_input/dim/dim_region.csv"
DIM_DATE = "/home/arouser/project-bi-uas/airflow_etl/data_input/dim/dim_date.csv"
DIM_CHANNEL = "/home/arouser/project-bi-uas/airflow_etl/data_input/dim/dim_channel.csv"

OUTPUT_KONTRIBUSI = "/home/arouser/project-bi-uas/airflow_etl/data_output/dwh_kontribusi_detailed.csv"
DJANGO_KONTRIBUSI = "/home/arouser/project-bi-uas/django_dashboard/biapp/data/dwh_kontribusi_detailed.csv"

def extract():
    df = pd.read_csv(FACT_KONTRIBUSI)
    df = df.merge(pd.read_csv(DIM_REGION), on="id_region", how="left")
    df = df.merge(pd.read_csv(DIM_DATE), on="id_date", how="left")
    df = df.merge(pd.read_csv(DIM_CHANNEL), on="channel_key", how="left")

    os.makedirs(os.path.dirname(OUTPUT_KONTRIBUSI), exist_ok=True)
    df.to_csv(OUTPUT_KONTRIBUSI, index=False)

# Step 2: Transform sesuai kebutuhan grafik kontribusi wilayah
def transform():
    df = pd.read_csv(OUTPUT_KONTRIBUSI)

    # Hitung total qty per wilayah/provinsi
    df_kontribusi = df.groupby("provinsi")["qty"].sum().reset_index()
    df_kontribusi.rename(columns={"qty": "total_qty"}, inplace=True)

    df_kontribusi.to_csv(OUTPUT_KONTRIBUSI, index=False)

# Step 3: Load to Django
def load():
    df = pd.read_csv(OUTPUT_KONTRIBUSI)
    os.makedirs(os.path.dirname(DJANGO_KONTRIBUSI), exist_ok=True)
    df.to_csv(DJANGO_KONTRIBUSI, index=False)

with DAG(
    dag_id="etl_kontribusi_detailed",
    start_date=datetime(2024, 1, 1),
    schedule="@weekly",
    catchup=False
) as dag:
    t1 = PythonOperator(task_id="extract", python_callable=extract)
    t2 = PythonOperator(task_id="transform", python_callable=transform)
    t3 = PythonOperator(task_id="load", python_callable=load)

    t1 >> t2 >> t3
