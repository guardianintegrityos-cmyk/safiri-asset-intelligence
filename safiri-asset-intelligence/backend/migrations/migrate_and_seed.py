import os
import psycopg2

DB_URL = os.getenv('DATABASE_URL', 'postgres://safiri:safiri123@localhost:5432/safiri_db')

CREATE_SQL = '001_create_tables.sql'
SAMPLE_SQL = 'sample_data.sql'


def run_sql_file(conn, filename):
    with open(filename, 'r') as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def main():
    conn = psycopg2.connect(DB_URL)
    run_sql_file(conn, CREATE_SQL)
    run_sql_file(conn, SAMPLE_SQL)
    print('Migration and sample data loaded.')
    conn.close()

if __name__ == '__main__':
    main()
