from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def extract_assets():
    print("Extracting unclaimed assets from institutions...")

def transform_data():
    print("Normalizing names, addresses, IDs...")

def load_data():
    print("Loading data into Postgres and Elasticsearch...")

default_args = {
    'owner': 'safiri',
    'depends_on_past': False,
    'start_date': datetime(2026,3,9),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG('asset_matching_dag',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    t1 = PythonOperator(task_id='extract_assets', python_callable=extract_assets)
    t2 = PythonOperator(task_id='transform_data', python_callable=transform_data)
    t3 = PythonOperator(task_id='load_data', python_callable=load_data)

    t1 >> t2 >> t3