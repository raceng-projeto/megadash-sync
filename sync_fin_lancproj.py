#!/usr/bin/env python3
"""Sincroniza FIN_LANCPROJ (lançamento x projeto)."""
import sys, time
from _common import fetch_oracle, post_chunks, log_sync, commit_swap

SQL = """
SELECT
    MOV_IN_NUMLANCTO  AS num_lancto,
    PRO_IN_REDUZIDO   AS projeto_codigo,
    LCL_CH_NATUREZA   AS natureza,
    LPR_RE_PERCENTUAL AS percentual,
    LPR_RE_VALOR      AS valor,
    LPR_RE_VALORCRE   AS valor_credito,
    LPR_RE_VALORDEB   AS valor_debito
FROM MEGA.FIN_LANCPROJ@RAC
WHERE PRO_PAD_IN_CODIGO = 1
"""

def main():
    started = time.time()
    print("\n=== fin_lancamento_projeto ===")
    try:
        rows = fetch_oracle(SQL)
        print(f"  {len(rows)} registros lidos")
        total = post_chunks("sync-fin-lancproj", rows)
        if total > 0:
            commit_swap("fin_lancamento_projeto")
        print(f"  ✅ {total} enviados em {time.time()-started:.1f}s")
        log_sync("fin_lancamento_projeto", total, "success")
    except Exception as e:
        print(f"  ❌ {e}", file=sys.stderr)
        log_sync("fin_lancamento_projeto", 0, "error", str(e))
        raise

if __name__ == "__main__":
    main()