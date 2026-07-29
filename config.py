# Configuração do sync MegaDash → Supabase
# Segredos vêm de variáveis de ambiente — ver .env.example.
# run_all.sh carrega .env automaticamente; pra rodar um script manualmente,
# faça `set -a; source .env; set +a` antes.
import os

# Oracle
ORACLE_USER = os.environ.get("ORACLE_USER", "RAC")
ORACLE_PASSWORD = os.environ["ORACLE_PASSWORD"]
ORACLE_DSN = os.environ.get("ORACLE_DSN", "dbconnect.megaerp.online:4221/xepdb1")
INSTANT_CLIENT_DIR = os.environ.get("INSTANT_CLIENT_DIR", "/opt/megadash-sync/instantclient")

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://fkcvhrgxwnuioszfukar.supabase.co")
SYNC_API_KEY = os.environ["SYNC_API_KEY"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]

# Chunks (registros por POST)
CHUNK_SIZE = 5000

# Timeout HTTP (segundos)
HTTP_TIMEOUT = 300
