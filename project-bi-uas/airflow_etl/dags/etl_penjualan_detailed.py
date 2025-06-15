from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime
import pandas as pd
import os

# Lokasi data
FACT_INPUT = "/home/arouser/project-bi-uas/airflow_etl/data_input/fact/fact_sales.csv"
DIM_PRODUCT = "/home/arouser/project-bi-uas/airflow_etl/data_input/dim/dim_product.csv"
DIM_REGION = "/home/arouser/project-bi-uas/airflow_etl/data_input/dim/dim_region.csv"
DIM_DATE = "/home/arouser/project-bi-uas/airflow_etl/data_input/dim/dim_date.csv"
OUTPUT_PATH = "/home/arouser/project-bi-uas/airflow_etl/data_output/dwh_penjualan_detailed.csv"
DJANGO_DATA = "/home/arouser/project-bi-uas/django_dashboard/biapp/data/dwh_penjualan_detailed.csv"

def extract_and_join():
    fact_df = pd.read_csv(FACT_INPUT)
    dim_product = pd.read_csv(DIM_PRODUCT)
    dim_region = pd.read_csv(DIM_REGION)
    dim_date = pd.read_csv(DIM_DATE)

    # Join dengan dimensi
    df = fact_df.merge(dim_product, on="id_product", how="left")
    df = df.merge(dim_region, on="id_region", how="left")
    df = df.merge(dim_date, on="id_date", how="left")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

def transform():
    df = pd.read_csv(OUTPUT_PATH)
    df["total_penjualan"] = df["qty"] * df["harga"]
    df.to_csv(OUTPUT_PATH, index=False)

def load():
    df = pd.read_csv(OUTPUT_PATH)
    os.makedirs(os.path.dirname(DJANGO_DATA), exist_ok=True)
    df.to_csv(DJANGO_DATA, index=False)

# Define DAG
with DAG(
    dag_id='etl_penjualan_detailed',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False
) as dag:
    t1 = PythonOperator(task_id='extract_and_join', python_callable=extract_and_join)
    t2 = PythonOperator(task_id='transform', python_callable=transform)
    t3 = PythonOperator(task_id='load', python_callable=load)

# Trigger DAG etl_model5g setelah load selesai
    t4 = TriggerDagRunOperator(
        task_id='trigger_model5g',
        trigger_dag_id='etl_model5g_detailed',
        wait_for_completion=True
    )

    t1 >> t2 >> t3 >> t4
