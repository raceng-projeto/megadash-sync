import oracledb
from config import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, INSTANT_CLIENT_DIR

oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
cur = conn.cursor()

print("=== TODAS as tabelas MEGA.FIN_* via @RAC ===")
cur.execute("""
    SELECT TABLE_NAME
    FROM ALL_TABLES@RAC
    WHERE OWNER='MEGA' AND TABLE_NAME LIKE 'FIN_%'
    ORDER BY TABLE_NAME
""")
tables = [r[0] for r in cur.fetchall()]
for t in tables:
    print(t)

print(f"\nTotal: {len(tables)}")

# Focar nas candidatas para retenção e baixa
keywords = ['RETEN', 'BAIXA', 'IMPOSTO', 'TRIBUT', 'LIQUIDAC', 'PAGAMENTO', 'RECEBIMENTO',
            'CTATAB', 'CTA_TAB', 'EXTRAT', 'MOV_BANC', 'BANCO', 'CONTA']
print("\n=== Candidatas (contêm palavras-chave) ===")
for t in tables:
    for kw in keywords:
        if kw in t.upper():
            print(f"  {t}  [{kw}]")
            break

conn.close()
