from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from pipelines.nigeria_ingest import ingest_ufaa, ingest_bank, ingest_insurer

default_args = {
    'owner': 'safiri',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10)
}

dag = DAG('safiri_nigeria_etl', default_args=default_args, schedule_interval='@daily', start_date=datetime(2026,3,1))

t1 = PythonOperator(task_id='ufaa_ingest', python_callable=ingest_ufaa, dag=dag)
t2 = PythonOperator(task_id='bank_ingest', python_callable=ingest_bank, dag=dag)
t3 = PythonOperator(task_id='insurer_ingest', python_callable=ingest_insurer, dag=dag)

t1 >> t2 >> t3
