"""
Update Cashier Full Name to 'Hemanth' in Supabase PostgreSQL
"""
import psycopg2
from config import Config

def update_cashier():
    print("[UPDATING] Connecting to Supabase PostgreSQL...")
    conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("""
        UPDATE public.profiles 
        SET full_name = 'Hemanth' 
        WHERE email = 'cashier@freshcut.com' OR pin = '5678'
        RETURNING id, email, full_name, role, pin;
    """)
    rows = cur.fetchall()
    for row in rows:
        print(f"  -> Updated Cashier Profile: ID={row[0]} | Email={row[1]} | Name={row[2]} | Role={row[3]} | PIN={row[4]}")

    cur.close()
    conn.close()
    print("[SUCCESS] Cashier name updated to HEMANTH in Supabase.")

if __name__ == '__main__':
    update_cashier()
