import oracledb
from config import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, INSTANT_CLIENT_DIR

oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
cur = conn.cursor()

print("=== Usuario atual ===")
cur.execute("SELECT USER FROM DUAL")
print(cur.fetchone())

print("\n=== DB Links disponiveis ===")
cur.execute("SELECT DB_LINK, USERNAME, HOST FROM USER_DB_LINKS")
for r in cur.fetchall():
    print(r)

print("\n=== Owners com tabelas FIN_ via @RAC ===")
try:
    cur.execute("SELECT DISTINCT OWNER, COUNT(*) FROM ALL_TABLES@RAC WHERE TABLE_NAME LIKE 'FIN_%' GROUP BY OWNER ORDER BY 2 DESC")
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print("Erro ALL_TABLES@RAC:", e)

print("\n=== Tabelas FIN_ acessiveis sem link ===")
try:
    cur.execute("SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE TABLE_NAME LIKE 'FIN_%' ORDER BY OWNER, TABLE_NAME")
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print("Erro:", e)

print("\n=== Schemas com FIN_MOVIMENTO ===")
try:
    cur.execute("SELECT OWNER FROM ALL_TABLES WHERE TABLE_NAME = 'FIN_MOVIMENTO'")
    for r in cur.fetchall():
        print(r)
    cur.execute("SELECT OWNER FROM ALL_TABLES@RAC WHERE TABLE_NAME = 'FIN_MOVIMENTO'")
    for r in cur.fetchall():
        print("via @RAC:", r)
except Exception as e:
    print("Erro:", e)

print("\n=== Teste SELECT atual na FIN_MOVIMENTO via RAC (5 colunas, 1 row) ===")
try:
    cur.execute("SELECT * FROM MEGA.FIN_MOVIMENTO@RAC WHERE ROWNUM <= 1")
    cols = [c[0] for c in cur.description]
    row = cur.fetchone()
    print("Colunas:", cols[:10], "...")
except Exception as e:
    print("Erro FIN_MOVIMENTO@RAC:", e)
    # Tenta sem schema
    try:
        cur.execute("SELECT * FROM FIN_MOVIMENTO@RAC WHERE ROWNUM <= 1")
        cols = [c[0] for c in cur.description]
        print("(sem MEGA.) Colunas:", cols[:10])
    except Exception as e2:
        print("Erro sem MEGA.:", e2)

conn.close()
print("\nFim.")
