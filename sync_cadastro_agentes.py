#!/usr/bin/env python3
"""Sincroniza GLO_AGENTES (clientes/fornecedores)."""
import sys, time
from _common import fetch_oracle, post_chunks, log_sync, commit_swap

SQL = """
SELECT
    AGN_IN_CODIGO       AS codigo,
    AGN_ST_NOME         AS nome,
    AGN_ST_FANTASIA     AS fantasia,
    AGN_ST_CGC          AS cgc,
    AGN_CH_TIPOPESSOAFJ AS tipo_pessoa,
    AGN_ST_EMAIL        AS email,
    AGN_ST_MUNICIPIO    AS municipio,
    UF_ST_SIGLA         AS uf
FROM MEGA.GLO_AGENTES@RAC
WHERE AGN_PAD_IN_CODIGO = 1
"""

def _s(v):
    if v is None: return None
    v = str(v).strip()
    return v or None

def main():
    started = time.time()
    print("\n=== cadastro_agentes ===")
    try:
        rows = fetch_oracle(SQL)
        print(f"  {len(rows)} registros lidos")
        records = [{
            "codigo": r["codigo"],
            "nome": _s(r["nome"]) or "",
            "fantasia": _s(r["fantasia"]),
            "cgc": _s(r["cgc"]),
            "tipo_pessoa": _s(r["tipo_pessoa"]),
            "email": _s(r["email"]),
            "municipio": _s(r["municipio"]),
            "uf": _s(r["uf"]),
        } for r in rows if r["codigo"] is not None]
        total = post_chunks("sync-cadastro-agentes", records)
        if total > 0:
            commit_swap("cadastro_agentes")
        print(f"  ✅ {total} enviados em {time.time()-started:.1f}s")
        log_sync("cadastro_agentes", total, "success")
    except Exception as e:
        print(f"  ❌ {e}", file=sys.stderr)
        log_sync("cadastro_agentes", 0, "error", str(e))
        raise

if __name__ == "__main__":
    main()