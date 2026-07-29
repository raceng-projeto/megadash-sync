#!/usr/bin/env python3
"""
Descobre tabelas Oracle do Mega relacionadas a retenções, baixas e conta corrente.
Execute UMA VEZ na VPS para confirmar os nomes reais antes de escrever os SQLs de sync.

Uso:
  ./venv/bin/python discover_oracle.py

A saída lista: tabela | coluna | tipo — filtre pelo que você precisa.
"""
import oracledb
from config import ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, INSTANT_CLIENT_DIR

oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
cur = conn.cursor()

PATTERNS = [
    "%FIN%RETEN%",
    "%FIN%BAIXA%",
    "%FIN%CTA%CORR%",
    "%FIN%MOV%BANC%",
    "%FIN%EXTRAT%",
    "%FIN%IMPOSTO%",
    "%FIN%LIQUIDAC%",
    "%FIN%PAGAMENT%",
]

found_tables = set()
for pat in PATTERNS:
    cur.execute(
        "SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER='MEGA' AND TABLE_NAME LIKE :p ORDER BY TABLE_NAME",
        p=pat,
    )
    for (tname,) in cur.fetchall():
        found_tables.add(tname)

if not found_tables:
    print("Nenhuma tabela encontrada com os padrões usados. Listando TODAS as tabelas FIN_* do owner MEGA:")
    cur.execute(
        "SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER='MEGA' AND TABLE_NAME LIKE 'FIN\\_%' ESCAPE '\\' ORDER BY TABLE_NAME"
    )
    for (t,) in cur.fetchall():
        print(f"  {t}")
else:
    print(f"Tabelas encontradas ({len(found_tables)}):\n")
    for tname in sorted(found_tables):
        print(f"{'='*60}")
        print(f"MEGA.{tname}")
        cur.execute(
            """
            SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, DATA_PRECISION, NULLABLE
            FROM ALL_COLUMNS
            WHERE OWNER='MEGA' AND TABLE_NAME=:t
            ORDER BY COLUMN_ID
            """,
            t=tname,
        )
        for col, dtype, dlen, dprec, nullable in cur.fetchall():
            print(f"  {col:<35} {dtype}({dprec or dlen}) {'NULL' if nullable=='Y' else 'NOT NULL'}")
        # Amostra de 3 linhas
        try:
            cur.execute(f"SELECT * FROM MEGA.{tname}@RAC WHERE ROWNUM <= 3")
            cols = [c[0] for c in cur.description]
            rows = cur.fetchall()
            if rows:
                print(f"\n  Amostra ({len(rows)} linhas):")
                for r in rows:
                    print("  " + str(dict(zip(cols, r)))[:200])
        except Exception as e:
            print(f"  (erro ao amostrar via @RAC: {e})")

conn.close()
print("\nFim da descoberta.")
