import oracledb
from config import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, INSTANT_CLIENT_DIR

oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
cur = conn.cursor()

print("=== Tabelas MEGA.FIN_* que CONSULTAS pode SELECTar via @RAC ===")
# Consulta os privilégios de tabela do usuário conectado remotamente
try:
    cur.execute("""
        SELECT TABLE_NAME
        FROM ALL_TAB_PRIVS@RAC
        WHERE OWNER='MEGA'
          AND TABLE_NAME LIKE 'FIN_%'
          AND PRIVILEGE='SELECT'
        ORDER BY TABLE_NAME
    """)
    rows = cur.fetchall()
    print(f"Via ALL_TAB_PRIVS: {len(rows)} tabelas com SELECT")
    for r in rows:
        print(f"  {r[0]}")
except Exception as e:
    print(f"ALL_TAB_PRIVS@RAC erro: {e}")

print("\n=== USER_TAB_PRIVS (grants para CONSULTAS) ===")
try:
    cur.execute("""
        SELECT TABLE_NAME, PRIVILEGE
        FROM USER_TAB_PRIVS@RAC
        WHERE TABLE_NAME LIKE 'FIN_%'
        ORDER BY TABLE_NAME
    """)
    rows = cur.fetchall()
    for r in rows:
        print(f"  {r}")
except Exception as e:
    print(f"USER_TAB_PRIVS@RAC erro: {e}")

print("\n=== Roles do usuário CONSULTAS ===")
try:
    cur.execute("SELECT GRANTED_ROLE FROM USER_ROLE_PRIVS@RAC")
    for r in cur.fetchall():
        print(f"  {r[0]}")
except Exception as e:
    print(f"USER_ROLE_PRIVS@RAC erro: {e}")

print("\n=== Teste direto das tabelas candidatas ===")
# Testa SELECT 0 rows nas tabelas mais prováveis
candidates = [
    'FIN_BASESRET', 'FIN_FINANCANALITICO', 'FIN_FINANCANALITICOBX',
    'FIN_MOVFIN', 'FIN_BAIXAREFCPA', 'FIN_BAIXAREFCRE',
    'FIN_CONTASPAGAR', 'FIN_CONTASRECEBER',
    'FIN_LANCCLASSE', 'FIN_TRANSCLA', 'FIN_TRANSCCUSTO', 'FIN_TRANSPROJ',
    'FIN_DESCDUPLMOVFIN', 'FIN_DESCDUPL',
]
for t in candidates:
    try:
        cur.execute(f"SELECT COUNT(*) FROM MEGA.{t}@RAC WHERE ROWNUM <= 0")
        print(f"  {t}: OK (acesso confirmado)")
    except Exception as e:
        msg = str(e).split('\n')[0]
        print(f"  {t}: ERRO - {msg}")

conn.close()
