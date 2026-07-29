import oracledb
from config import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, INSTANT_CLIENT_DIR

oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
cur = conn.cursor()

print("=== FIN_FINANCANALITICO — distinct NUMLANCTOs (tipo Movimento) ===")
cur.execute("""
    SELECT COUNT(DISTINCT MOV_IN_NUMLANCTO),
           MIN(MOV_IN_NUMLANCTO),
           MAX(MOV_IN_NUMLANCTO)
    FROM MEGA.FIN_FINANCANALITICO@RAC
    WHERE MOV_ST_TIPOLINHA = 'Movimento'
""")
r = cur.fetchone()
print(f"  Distinct: {r[0]} | Min: {r[1]} | Max: {r[2]}")

print("\n=== FIN_FINANCANALITICOBX — distinct combos ===")
cur.execute("""
    SELECT COUNT(DISTINCT MOV_IN_NUMLANCTO || '|' || NVL(REF_ST_TIPO,'') || '|' ||
                          NVL(TO_CHAR(MOV_DT_DATADOCTOBX,'YYYYMMDD'),'') || '|' ||
                          NVL(TO_CHAR(MOV_RE_VALORBX),''))
    FROM MEGA.FIN_FINANCANALITICOBX@RAC
""")
r = cur.fetchone()
print(f"  Distinct combos: {r[0]}")

print("\n=== Amostra com retencoes reais ===")
cur.execute("""
    SELECT MOV_IN_NUMLANCTO, CPA_IN_AP, FIL_ST_FANTASIA,
           AGN_ST_FANTASIA, TPD_ST_CODIGO, MOV_ST_DOCUMENTO,
           MOV_RE_VALOR, MOV_RE_IR, MOV_RE_INSS, MOV_RE_ISS,
           MOV_RE_PIS, MOV_RE_COFINS, MOV_RE_CSLL,
           MOV_RE_TOTALRETENCAO, MOV_RE_TOTALBAIXA, MOV_RE_ABERTO
    FROM MEGA.FIN_FINANCANALITICO@RAC
    WHERE MOV_ST_TIPOLINHA = 'Movimento'
      AND (MOV_RE_IR > 0 OR MOV_RE_INSS > 0 OR MOV_RE_ISS > 0
           OR MOV_RE_PIS > 0 OR MOV_RE_COFINS > 0)
      AND ROWNUM <= 5
""")
cols = [c[0] for c in cur.description]
for row in cur.fetchall():
    print(dict(zip(cols, [str(v)[:30] if v is not None else None for v in row])))

conn.close()
print("\nFim.")
