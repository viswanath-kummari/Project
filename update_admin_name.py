"""
Update Admin Full Name to 'Viswanath' in Supabase PostgreSQL
"""
import psycopg2
from config import Config

def update_admin():
    print("[UPDATING] Connecting to Supabase PostgreSQL...")
    conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    conn.autocommit = True
    cur = conn.cursor()

    # Update admin user name
    cur.execute("""
        UPDATE public.profiles 
        SET full_name = 'Viswanath' 
        WHERE email = 'admin@freshcut.com' OR role = 'admin'
        RETURNING id, email, full_name, role;
    """)
    rows = cur.fetchall()
    for row in rows:
        print(f"  -> Updated Admin Profile: ID={row[0]} | Email={row[1]} | Name={row[2]} | Role={row[3]}")

    cur.close()
    conn.close()
    print("[SUCCESS] Admin name updated to VISWANATH in Supabase.")

if __name__ == '__main__':
    update_admin()
