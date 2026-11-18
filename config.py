import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fresh-cut-super-secure-production-jwt-key-2026")
    JWT_SECRET = os.getenv("JWT_SECRET", "fresh-cut-meat-jwt-secret-token-key-2026")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Database Configuration (Falls back to local SQLite if Supabase URL not provided)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'freshcut.db')}"
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Business Defaults
    SHOP_NAME = os.getenv("SHOP_NAME", "Fresh Cut Artisanal Meat Co.")
    SHOP_TAGLINE = os.getenv("SHOP_TAGLINE", "Prime Cuts, Poultry & Farm-Fresh Seafood")
    SHOP_PHONE = os.getenv("SHOP_PHONE", "+91 98765 43210")
    SHOP_ADDRESS = os.getenv("SHOP_ADDRESS", "Plot 42, Gourmet Boulevard, Market District")
    SHOP_GST_NO = os.getenv("SHOP_GST_NO", "36AAAAA0000A1Z5")
    DEFAULT_TAX_PERCENT = float(os.getenv("DEFAULT_TAX_PERCENT", "5.0"))
    CURRENCY_SYMBOL = os.getenv("CURRENCY_SYMBOL", "₹")
    INVOICE_PREFIX = os.getenv("INVOICE_PREFIX", "FC-")
