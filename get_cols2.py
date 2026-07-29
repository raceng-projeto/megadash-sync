import oracledb
from config import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, INSTANT_CLIENT_DIR

oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
cur = conn.cursor()

TABLES = [
    'FIN_FINANCANALITICO',
    'FIN_FINANCANALITICOBX',
    'FIN_BASESRET',
    'FIN_MOVFIN',
    'FIN_BAIXAREFCPA',
    'FIN_BAIXAREFCRE',
    'FIN_CONTASRECEBER',
    'FIN_CONTASPAGAR',
    'FIN_LANCCLASSE',
]

for tname in TABLES:
    print(f"\n{'='*70}")
    print(f"MEGA.{tname}")
    try:
        cur.execute(f"SELECT * FROM MEGA.{tname}@RAC WHERE 1=0")
        cols = [c[0] for c in cur.description]
        for i, col in enumerate(cols):
            print(f"  {i+1:3}. {col}")
        # Sample
        cur.execute(f"SELECT * FROM MEGA.{tname}@RAC WHERE ROWNUM <= 2")
        srows = cur.fetchall()
        if srows:
            print(f"  --- Amostra ({len(srows)} linhas) ---")
            for sr in srows:
                d = {k: str(v)[:50] for k, v in zip(cols, sr) if v is not None and v != 0}
                print("  " + str(d)[:500])
    except Exception as e:
        print(f"  ERRO: {e}")

conn.close()
print("\nFim.")
