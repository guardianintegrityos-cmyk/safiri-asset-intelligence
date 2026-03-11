from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from etl_scripts import ingest_data, clean_data, enrich_data, load_to_db

def decide_enrichment(**kwargs):
    if kwargs['dag_run'].conf.get('skip_enrich'):
        return 'load'
    return 'enrich'

dag = DAG('nigeria_etl', start_date=datetime(2026, 3, 1), schedule_interval='@daily')
ingest = PythonOperator(task_id='ingest', python_callable=ingest_data, op_args=['nigeria'], dag=dag)
clean = PythonOperator(task_id='clean', python_callable=clean_data, op_args=['nigeria'], dag=dag)
enrich = PythonOperator(task_id='enrich', python_callable=enrich_data, op_args=['nigeria'], dag=dag)
load = PythonOperator(task_id='load', python_callable=load_to_db, op_args=['nigeria'], dag=dag)
ingest >> clean >> enrich >> load
