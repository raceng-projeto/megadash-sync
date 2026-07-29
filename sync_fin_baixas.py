#!/usr/bin/env python3
"""Sincroniza baixas: FIN_FINANCANALITICOBX → fin_baixas.
83k baixas únicas (GROUP BY NUMLANCTO + TIPO + DATA).
Colunas: num_lancto, tipo, data_baixa, valor, natureza,
         conta_financeira_codigo, conta_financeira_fantasia, conta_financeira_razao.
"""
import time
from _common import fetch_oracle, post_chunks, log_sync, commit_swap

SQL = """
SELECT
    MOV_IN_NUMLANCTO                AS num_lancto,
    MAX(REF_ST_DESCRICAO)           AS tipo,
    MOV_DT_DATADOCTOBX              AS data_baixa,
    MAX(NVL(MOV_RE_VALORBX, 0))    AS valor,
    MAX(AGN_IN_CODIGOCTA)           AS conta_financeira_codigo,
    MAX(AGN_ST_FANTASIACTA)         AS conta_financeira_fantasia,
    MAX(AGN_ST_NOMECTA)             AS conta_financeira_razao
FROM MEGA.FIN_FINANCANALITICOBX@RAC
GROUP BY MOV_IN_NUMLANCTO, REF_ST_TIPO, MOV_DT_DATADOCTOBX
HAVING MAX(NVL(MOV_RE_VALORBX, 0)) > 0
ORDER BY MOV_IN_NUMLANCTO
"""


def transform(r: dict) -> dict:
    v = r.get('valor')
    r['valor'] = float(v) if v is not None else 0.0
    cod = r.get('conta_financeira_codigo')
    r['conta_financeira_codigo'] = int(cod) if cod is not None else None
    dt = r.get('data_baixa')
    if dt and hasattr(dt, 'strftime'):
        r['data_baixa'] = dt.strftime('%Y-%m-%d')
    return r


def main():
    started = time.time()
    print("\n=== sync_fin_baixas ===")
    try:
        print("  Lendo Oracle (FIN_FINANCANALITICOBX)…")
        rows = fetch_oracle(SQL)
        print(f"  {len(rows)} baixas únicas lidas. Enviando…")
        records = [transform(r) for r in rows]
        total = post_chunks("sync-fin-baixas", records)
        if total > 0:
            commit_swap("fin_baixas")
        print(f"  ✅ {total} enviados em {time.time()-started:.1f}s")
        log_sync("fin_baixas", total, "success")
    except Exception as e:
        print(f"  ❌ {e}")
        log_sync("fin_baixas", 0, "error", str(e))
        raise


if __name__ == "__main__":
    main()
