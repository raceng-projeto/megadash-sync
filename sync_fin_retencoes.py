#!/usr/bin/env python3
"""Sincroniza retenções: FIN_FINANCANALITICO → fin_retencoes.
Schema colunar: ir, inss, iss, pis, cofins, csll, cont_soc, sest_senat, caucao, funrural, total.
"""
import time
from _common import fetch_oracle, post_chunks, log_sync, commit_swap

SQL = """
SELECT
    MOV_IN_NUMLANCTO                           AS num_lancto,
    MAX(NVL(MOV_RE_IR,            0))          AS ir,
    MAX(NVL(MOV_RE_INSS,          0))          AS inss,
    MAX(NVL(MOV_RE_ISS,           0))          AS iss,
    MAX(NVL(MOV_RE_PIS,           0))          AS pis,
    MAX(NVL(MOV_RE_COFINS,        0))          AS cofins,
    MAX(NVL(MOV_RE_CSLL,          0))          AS csll,
    MAX(NVL(MOV_RE_PCC,           0))          AS cont_soc,
    MAX(NVL(MOV_RE_SEST,          0))          AS sest_senat,
    MAX(NVL(MOV_RE_CAUCAO,        0))          AS caucao,
    MAX(NVL(MOV_RE_FUNRURAL,      0))          AS funrural,
    MAX(NVL(MOV_RE_TOTALRETENCAO, 0))          AS total
FROM MEGA.FIN_FINANCANALITICO@RAC
WHERE MOV_ST_TIPOLINHA = 'Movimento'
GROUP BY MOV_IN_NUMLANCTO
HAVING MAX(NVL(MOV_RE_TOTALRETENCAO, 0)) > 0
ORDER BY MOV_IN_NUMLANCTO
"""


def transform(r: dict) -> dict:
    for col in ('ir', 'inss', 'iss', 'pis', 'cofins', 'csll',
                'cont_soc', 'sest_senat', 'caucao', 'funrural', 'total'):
        v = r.get(col)
        r[col] = float(v) if v is not None else 0.0
    return r


def main():
    started = time.time()
    print("\n=== sync_fin_retencoes ===")
    try:
        print("  Lendo Oracle (FIN_FINANCANALITICO)…")
        rows = fetch_oracle(SQL)
        print(f"  {len(rows)} títulos com retenção encontrados. Enviando…")
        records = [transform(r) for r in rows]
        total = post_chunks("sync-fin-retencoes", records)
        if total > 0:
            commit_swap("fin_retencoes")
        print(f"  ✅ {total} enviados em {time.time()-started:.1f}s")
        log_sync("fin_retencoes", total, "success")
    except Exception as e:
        print(f"  ❌ {e}")
        log_sync("fin_retencoes", 0, "error", str(e))
        raise


if __name__ == "__main__":
    main()
