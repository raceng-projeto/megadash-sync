#!/usr/bin/env python3
"""Sincroniza FIN_MOVIMENTO."""
import sys, time
from _common import fetch_oracle, post_chunks, log_sync, commit_swap

SQL = """
SELECT
    MOV_IN_NUMLANCTO    AS num_lancto,
    ORG_IN_CODIGO       AS org_codigo,
    MOV_CH_NATUREZA     AS natureza,
    TPD_ST_CODIGO       AS tipo_documento,
    MOV_ST_DOCUMENTO    AS documento,
    MOV_ST_PARCELA      AS parcela,
    MOV_DT_DATADOCTO    AS data_documento,
    MOV_DT_ENTRADA      AS data_entrada,
    MOV_DT_VENCTO       AS data_vencimento,
    MOV_RE_VALOR        AS valor,
    MOV_RE_VALORCRE     AS valor_credito,
    MOV_RE_VALORDEB     AS valor_debito,
    MOV_CH_STATUSSALDO  AS status_saldo,
    MOV_CH_SITUACAO     AS situacao,
    MOV_CH_STATUSMOV    AS status_mov,
    MOV_BO_PREVISAO     AS previsao,
    MOV_ST_COMPLHIST    AS complemento_historico,
    AGN_IN_CODIGO       AS agente_codigo,
    CONT_TAC_ST_CODIGO  AS cont_tac,
    MOV_CH_ORIGEM       AS origem
FROM MEGA.FIN_MOVIMENTO@RAC
WHERE MOV_CH_STATUSMOV = 'A'
"""

def transform(r):
    cont_tac = r.pop("cont_tac", None)
    origem = r.get("origem")
    if cont_tac == "CPAG" or origem == "P":
        r["tipo_conta"] = "pagar"
    elif cont_tac == "CREC" or origem in ("R", "F"):
        r["tipo_conta"] = "receber"
    else:
        r["tipo_conta"] = "outros"
    prev = r.get("previsao")
    r["previsao"] = (prev == "S") if isinstance(prev, str) else bool(prev)
    return r

def main():
    started = time.time()
    print("\n=== fin_movimentos ===")
    try:
        rows = fetch_oracle(SQL)
        print(f"  {len(rows)} registros lidos")
        records = [transform(r) for r in rows]
        total = post_chunks("sync-fin-movimentos", records)
        if total > 0:
            commit_swap("fin_movimentos")
        print(f"  ✅ {total} enviados em {time.time()-started:.1f}s")
        log_sync("fin_movimentos", total, "success")
    except Exception as e:
        print(f"  ❌ {e}", file=sys.stderr)
        log_sync("fin_movimentos", 0, "error", str(e))
        raise

if __name__ == "__main__":
    main()