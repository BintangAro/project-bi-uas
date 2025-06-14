from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime
import pandas as pd
import os

# Lokasi file input dan output
FACT_MODEL5G = "/home/arouser/project-bi-uas/airflow_etl/data_input/fact/fact_model5g.csv"
DIM_PRODUCT = "/home/arouser/project-bi-uas/airflow_etl/data_input/dim/dim_product.csv"
DIM_REGION = "/home/arouser/project-bi-uas/airflow_etl/data_input/dim/dim_region.csv"
DIM_DATE = "/home/arouser/project-bi-uas/airflow_etl/data_input/dim/dim_date.csv"

OUTPUT_MODEL5G = "/home/arouser/project-bi-uas/airflow_etl/data_output/dwh_model5g_detailed.csv"
DJANGO_MODEL5G = "/home/arouser/project-bi-uas/django_dashboard/biapp/data/dwh_model5g_detailed.csv"

# Step 1: Extract dan Join dengan dimensi
def extract():
    df = pd.read_csv(FACT_MODEL5G)
    df = df.merge(pd.read_csv(DIM_PRODUCT), on="id_product", how="left")
    df = df.merge(pd.read_csv(DIM_REGION), on="id_region", how="left")
    df = df.merge(pd.read_csv(DIM_DATE), on="id_date", how="left")
    
    os.makedirs(os.path.dirname(OUTPUT_MODEL5G), exist_ok=True)
    df.to_csv(OUTPUT_MODEL5G, index=False)

# Step 2: Transformasi (hitung revenue bersih)
def transform():
    df = pd.read_csv(OUTPUT_MODEL5G)
    df["revenue_bersih"] = df["revenue"] * (1 - df["diskon"] / 100)
    df.to_csv(OUTPUT_MODEL5G, index=False)

# Step 3: Load ke folder Django
def load():
    df = pd.read_csv(OUTPUT_MODEL5G)
    os.makedirs(os.path.dirname(DJANGO_MODEL5G), exist_ok=True)
    df.to_csv(DJANGO_MODEL5G, index=False)

# DAG Definition
with DAG(
    dag_id="etl_model5g_detailed",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False
) as dag:

    t1 = PythonOperator(task_id="extract", python_callable=extract)
    t2 = PythonOperator(task_id="transform", python_callable=transform)
    t3 = PythonOperator(task_id="load", python_callable=load)

    # Trigger kontribusi
    t4 = TriggerDagRunOperator(
        task_id='trigger_kontribusi',
        trigger_dag_id='etl_kontribusi_detailed',
        wait_for_completion=True
    )

    t1 >> t2 >> t3 >> t4