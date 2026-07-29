#!/usr/bin/env python3
"""Sincroniza FIN_LANCCCUSTO (lançamento x centro de custo)."""
import sys, time
from _common import fetch_oracle, post_chunks, log_sync, commit_swap

SQL = """
SELECT
    MOV_IN_NUMLANCTO AS num_lancto,
    ORG_IN_CODIGO    AS org_codigo,
    CCF_IN_REDUZIDO  AS centro_custo_codigo,
    CLA_IN_REDUZIDO  AS classificacao_codigo,
    LCL_CH_NATUREZA  AS natureza,
    LCC_RE_VALOR     AS valor,
    LCC_RE_VALORCRE  AS valor_credito,
    LCC_RE_VALORDEB  AS valor_debito,
    LCC_RE_PERCENTUAL AS percentual,
    LCC_ST_OBSERVACAO AS observacao
FROM MEGA.FIN_LANCCCUSTO@RAC
"""

def main():
    started = time.time()
    print("\n=== fin_centro_custo ===")
    try:
        rows = fetch_oracle(SQL)
        print(f"  {len(rows)} registros lidos")
        total = post_chunks("sync-fin-centro-custo", rows)
        if total > 0:
            commit_swap("fin_centro_custo")
        print(f"  ✅ {total} enviados em {time.time()-started:.1f}s")
        log_sync("fin_centro_custo", total, "success")
    except Exception as e:
        print(f"  ❌ {e}", file=sys.stderr)
        log_sync("fin_centro_custo", 0, "error", str(e))
        raise

if __name__ == "__main__":
    main()