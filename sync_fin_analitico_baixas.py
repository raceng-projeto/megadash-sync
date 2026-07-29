"""Sync FIN_FINANCANALITICOBX → Supabase fin_analitico_baixas.
~83 k baixas únicas. GROUP BY para desduplicar sessões Oracle.
"""
import time
from _common import fetch_oracle, post_chunks, commit_swap, log_sync

ENDPOINT = "sync-fin-analitico-baixas"
TABLE    = "fin_analitico_baixas"

SQL = """
SELECT
    MOV_IN_NUMLANCTO            AS num_lancto,
    REF_ST_TIPO                 AS tipo,
    MAX(REF_ST_DESCRICAO)       AS descricao,
    MOV_DT_DATADOCTOBX          AS data_baixa,
    MAX(NVL(MOV_RE_VALORBX, 0)) AS valor,
    MAX(AGN_IN_CODIGOCTA)       AS conta_codigo,
    MAX(AGN_ST_NOMECTA)         AS conta_nome,
    MAX(AGN_ST_FANTASIACTA)     AS conta_fantasia
FROM MEGA.FIN_FINANCANALITICOBX@RAC
GROUP BY MOV_IN_NUMLANCTO, REF_ST_TIPO, MOV_DT_DATADOCTOBX
ORDER BY MOV_IN_NUMLANCTO
"""

def main():
    started = time.time()
    print("\n=== sync_fin_analitico_baixas ===")
    try:
        print("  Lendo Oracle…")
        rows = fetch_oracle(SQL)
        print(f"  {len(rows)} baixas únicas lidas. Enviando…")
        total = post_chunks(ENDPOINT, rows)
        if total > 0:
            commit_swap(TABLE)
        print(f"  ✅ {total} enviados em {time.time()-started:.1f}s")
        log_sync(TABLE, total, "success")
    except Exception as e:
        print(f"  ❌ {e}")
        log_sync(TABLE, 0, "error", str(e))
        raise

if __name__ == "__main__":
    main()
