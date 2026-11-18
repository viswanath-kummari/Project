"""
Update product image URLs in Supabase PostgreSQL
"""
import psycopg2
from config import Config

IMAGES = {
    'CHK-BRS-01': 'https://images.unsplash.com/photo-1604503468506-a8da13d82791?auto=format&fit=crop&w=400&q=80',
    'CHK-CUR-02': 'https://images.unsplash.com/photo-1587593810167-a84920ea0781?auto=format&fit=crop&w=400&q=80',
    'CHK-DRM-03': 'https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=400&q=80',
    'CHK-WNG-04': 'https://images.unsplash.com/photo-1567620832903-9fc6debc209f?auto=format&fit=crop&w=400&q=80',
    'CHK-WHL-05': 'https://images.unsplash.com/photo-1516684732162-798a0062be99?auto=format&fit=crop&w=400&q=80',
    'MUT-CUR-01': 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=400&q=80',
    'MUT-CHP-02': 'https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=400&q=80',
    'MUT-MNC-03': 'https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?auto=format&fit=crop&w=400&q=80',
    'MUT-LVR-04': 'https://images.unsplash.com/photo-1588347818036-558601350947?auto=format&fit=crop&w=400&q=80',
    'SEA-PRW-01': 'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?auto=format&fit=crop&w=400&q=80',
    'SEA-SLM-02': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?auto=format&fit=crop&w=400&q=80',
    'SEA-SUR-03': 'https://images.unsplash.com/photo-1534483509719-3feaee7c30da?auto=format&fit=crop&w=400&q=80',
    'DEL-MAR-01': 'https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=400&q=80',
    'DEL-SAS-02': 'https://images.unsplash.com/photo-1541544741938-0af808871cc0?auto=format&fit=crop&w=400&q=80',
}

def update_images():
    print("[UPDATING] Connecting to Supabase...")
    conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    conn.autocommit = True
    cur = conn.cursor()

    updated = 0
    for sku, url in IMAGES.items():
        cur.execute("UPDATE products SET image_url = %s WHERE sku = %s RETURNING sku, name", (url, sku))
        row = cur.fetchone()
        if row:
            print(f"  -> Updated {row[0]}: {row[1]}")
            updated += 1
        else:
            print(f"  -> WARNING: Product {sku} not found!")

    print(f"[DONE] Updated {updated} products with high-resolution meat photography.")
    cur.close()
    conn.close()

if __name__ == '__main__':
    update_images()
