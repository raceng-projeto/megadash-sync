#!/usr/bin/env python3
"""Sincroniza GLO_PROJETOS (árvore completa de projetos/obras)."""
import sys, time
from _common import fetch_oracle, post_chunks, log_sync, commit_swap

SQL = """
SELECT
    PRO_IN_REDUZIDO      AS codigo,
    PRO_ST_DESCRICAO     AS descricao,
    PRO_CH_ANASIN        AS status,
    PRO_IN_NIVEL         AS nivel,
    PAI_PRO_IN_REDUZIDO  AS projeto_pai
FROM MEGA.GLO_PROJETOS@RAC
"""

def main():
    started = time.time()
    print("\n=== cadastro_projetos ===")
    try:
        rows = fetch_oracle(SQL)
        print(f"  {len(rows)} registros lidos")
        records = [{
            "codigo": int(r["codigo"]),
            "descricao": r["descricao"],
            "status": r["status"] or "A",
            "nivel": int(r["nivel"]) if r["nivel"] is not None else None,
            "projeto_pai": int(r["projeto_pai"]) if r["projeto_pai"] is not None else None,
        } for r in rows if r["codigo"] is not None]
        total = post_chunks("sync-cadastro-projetos", records)
        if total > 0:
            commit_swap("cadastro_projetos")
        print(f"  ✅ {total} enviados em {time.time()-started:.1f}s")
        log_sync("cadastro_projetos", total, "success")
    except Exception as e:
        print(f"  ❌ {e}", file=sys.stderr)
        log_sync("cadastro_projetos", 0, "error", str(e))
        raise

if __name__ == "__main__":
    main()