# etl_dag_uganda.py
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime
from etl_scripts import ingest_data, clean_data, enrich_data, load_to_db

dag = DAG('uganda_etl', start_date=datetime(2026, 3, 1), schedule_interval='@daily')

def decide_enrichment(**kwargs):
    if kwargs['dag_run'].conf.get('skip_enrich'):
        return 'load'
    return 'enrich'

branch = BranchPythonOperator(
    task_id='branch_enrich',
    python_callable=decide_enrichment,
    provide_context=True,
    dag=dag
)

email_alert = EmailOperator(
    task_id='email_on_failure',
    to='admin@safiri.com',
    subject='Uganda ETL Failure',
    html_content='Uganda ETL DAG failed!',
    dag=dag
)

ingest = PythonOperator(task_id='ingest', python_callable=ingest_data, op_args=['uganda'], dag=dag)
clean = PythonOperator(task_id='clean', python_callable=clean_data, op_args=['uganda'], dag=dag)
enrich = PythonOperator(task_id='enrich', python_callable=enrich_data, op_args=['uganda'], dag=dag)
load = PythonOperator(task_id='load', python_callable=load_to_db, op_args=['uganda'], dag=dag)

for task in [ingest, clean, enrich, load]:
    task.retries = 2
    task.email_on_failure = True
    task.email = ['admin@safiri.com']

ingest >> clean >> branch
branch >> enrich >> load
branch >> load
load >> email_alert
