import psycopg2

conn_str = 'postgresql://postgres:Viswanath%40321@db.hznrmvplqpgmgysizngt.supabase.co:5432/postgres'

print('[1/3] Reading supabase_setup.sql...')
with open('supabase_setup.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

print('[2/3] Connecting to Supabase and executing schema DDL...')
conn = psycopg2.connect(conn_str)
conn.autocommit = True
cur = conn.cursor()
cur.execute(sql)
print('[SUCCESS] supabase_setup.sql executed cleanly!')

print('[3/3] Inspecting public tables created in Supabase...')
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
tables = [r[0] for r in cur.fetchall()]
print('Public tables in Supabase:')
for t in sorted(tables):
    print(f'  - {t}')

conn.close()
