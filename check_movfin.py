import oracledb
from config import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, INSTANT_CLIENT_DIR

oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
cur = conn.cursor()

print("=== FIN_MOVIMENTO — todas as colunas ===")
cur.execute("SELECT * FROM MEGA.FIN_MOVIMENTO@RAC WHERE 1=0")
for i, col in enumerate(cur.description):
    print(f"  {i+1:3}. {col[0]}")

print("\n=== FIN_FINANCANALITICO — total e distinção de usuarios ===")
cur.execute("SELECT COUNT(*), COUNT(DISTINCT USU_IN_CODIGO), COUNT(DISTINCT COMP_ST_NOME) FROM MEGA.FIN_FINANCANALITICO@RAC")
r = cur.fetchone()
print(f"  Total linhas: {r[0]} | Usuários: {r[1]} | Computadores: {r[2]}")

print("\n=== FIN_FINANCANALITICO — range de datas e amostra ===")
cur.execute("""
    SELECT MIN(MOV_DT_VENCIMENTO), MAX(MOV_DT_VENCIMENTO),
           MIN(MOV_IN_NUMLANCTO), MAX(MOV_IN_NUMLANCTO),
           COUNT(DISTINCT MOV_IN_NUMLANCTO)
    FROM MEGA.FIN_FINANCANALITICO@RAC
    WHERE MOV_ST_TIPOLINHA IS NULL OR MOV_ST_TIPOLINHA = 'T'
""")
r = cur.fetchone()
print(f"  Vencto range: {r[0]} a {r[1]}")
print(f"  Lancto range: {r[2]} a {r[3]} | Distinct: {r[4]}")

print("\n=== FIN_FINANCANALITICOBX — total ===")
cur.execute("SELECT COUNT(*), COUNT(DISTINCT MOV_IN_NUMLANCTO) FROM MEGA.FIN_FINANCANALITICOBX@RAC")
r = cur.fetchone()
print(f"  Total: {r[0]} | Distinct lanctos: {r[1]}")

print("\n=== FIN_FINANCANALITICO — tipos de linha (MOV_ST_TIPOLINHA) ===")
cur.execute("SELECT MOV_ST_TIPOLINHA, COUNT(*) FROM MEGA.FIN_FINANCANALITICO@RAC GROUP BY MOV_ST_TIPOLINHA ORDER BY 2 DESC")
for r in cur.fetchall():
    print(f"  {r}")

print("\n=== FIN_FINANCANALITICO — amostra de linha tipo titulo (5 rows) ===")
cur.execute("""
    SELECT MOV_IN_NUMLANCTO, ORG_IN_CODIGO, FIL_ST_FANTASIA, AGN_IN_CODIGO,
           AGN_ST_FANTASIA, MOV_DT_VENCIMENTO, TPD_ST_CODIGO, MOV_ST_DOCUMENTO,
           MOV_RE_VALOR, MOV_RE_IR, MOV_RE_INSS, MOV_RE_ISS, MOV_RE_PIS, MOV_RE_COFINS,
           MOV_RE_CSLL, MOV_RE_TOTALRETENCAO, MOV_RE_TOTALBAIXA, MOV_RE_ABERTO,
           MOV_ST_TIPOLINHA
    FROM MEGA.FIN_FINANCANALITICO@RAC
    WHERE ROWNUM <= 5
""")
cols = [c[0] for c in cur.description]
for row in cur.fetchall():
    print(dict(zip(cols, [str(v)[:30] if v is not None else None for v in row])))

conn.close()
print("\nFim.")
