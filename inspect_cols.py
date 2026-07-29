import oracledb
from config import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, INSTANT_CLIENT_DIR

oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
cur = conn.cursor()

TABLES = [
    'FIN_FINANCANALITICO',
    'FIN_FINANCANALITICOBX',
    'FIN_FINANCANALITICOCLA',
    'FIN_FINANCANALITICOCUS',
    'FIN_FINANCANALITICOPRO',
    'FIN_BASESRET',
    'FIN_MOVFIN',
    'FIN_BAIXAREFCPA',
    'FIN_BAIXAREFCRE',
    'FIN_CONTASPAGAR',
    'FIN_CONTASRECEBER',
]

for tname in TABLES:
    print(f"\n{'='*60}")
    print(f"MEGA.{tname}")
    try:
        cur.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_PRECISION, NULLABLE
            FROM ALL_COLUMNS@RAC
            WHERE OWNER='MEGA' AND TABLE_NAME=:t
            ORDER BY COLUMN_ID
        """, t=tname)
        rows = cur.fetchall()
        for col, dtype, dlen, dprec, nullable in rows:
            print(f"  {col:<40} {dtype}({dprec or dlen})")
        # Sample row
        try:
            cur.execute(f"SELECT * FROM MEGA.{tname}@RAC WHERE ROWNUM <= 2")
            cols2 = [c[0] for c in cur.description]
            srows = cur.fetchall()
            if srows:
                print(f"  -- Amostra --")
                for sr in srows:
                    print("  " + str(dict(zip(cols2, sr)))[:300])
        except Exception as e2:
            print(f"  (amostra erro: {e2})")
    except Exception as e:
        print(f"  ERRO: {e}")

conn.close()
print("\nFim.")
