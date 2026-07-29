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
        # Get columns via describe trick
        cur.execute(f"SELECT * FROM MEGA.{tname}@RAC WHERE 1=0")
        cols = [(i+1, c[0], c[1].__name__ if c[1] else 'UNK') for i, c in enumerate(cur.description)]
        for num, col, typ in cols:
            print(f"  {num:3}. {col:<45} {typ}")
        # Sample 2 rows
        cur.execute(f"SELECT * FROM MEGA.{tname}@RAC WHERE ROWNUM <= 2")
        srows = cur.fetchall()
        colnames = [c[0] for c in cur.description]
        if srows:
            print(f"  --- Amostra ({len(srows)} linhas) ---")
            for sr in srows:
                d = {k: v for k, v in zip(colnames, sr)}
                # Print non-null fields only
                non_null = {k: str(v)[:60] for k, v in d.items() if v is not None and v != 0}
                print("  " + str(non_null)[:400])
    except Exception as e:
        print(f"  ERRO: {e}")

conn.close()
print("\nFim.")
