from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from pipelines.uefa_ingest import ingest_ufaa
from pipelines.bank_ingest import ingest_banks
from pipelines.insurer_ingest import ingest_insurers

default_args = {
    'owner': 'safiri',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('safiri_etl', default_args=default_args, schedule_interval='@daily')

task_ufaa = PythonOperator(task_id='ingest_ufaa', python_callable=ingest_ufaa, dag=dag)
task_bank = PythonOperator(task_id='ingest_banks', python_callable=ingest_banks, dag=dag)
task_insurer = PythonOperator(task_id='ingest_insurers', python_callable=ingest_insurers, dag=dag)

task_ufaa >> task_bank >> task_insurer
