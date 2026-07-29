"""Sync FIN_FINANCANALITICO → Supabase fin_analitico.
~101 k títulos únicos (CP + CR). GROUP BY NUMLANCTO desduplicar sessões de relatório.
CP: ap IS NOT NULL  |  CR: ap IS NULL
"""
import time
from _common import fetch_oracle, post_chunks, commit_swap, log_sync

ENDPOINT = "sync-fin-analitico"
TABLE    = "fin_analitico"

SQL = """
SELECT
    MOV_IN_NUMLANCTO                          AS num_lancto,
    MAX(ORG_IN_CODIGO)                        AS org_codigo,
    MAX(FIL_IN_CODIGO)                        AS fil_codigo,
    MAX(FIL_ST_FANTASIA)                      AS fil_fantasia,
    MAX(AGN_IN_CODIGO)                        AS agn_codigo,
    MAX(AGN_ST_NOME)                          AS agn_nome,
    MAX(AGN_ST_FANTASIA)                      AS agn_fantasia,
    MAX(FAT_ST_FAVORECIDO)                    AS fat_favorecido,
    MAX(MOV_DT_DATADOCTO)                     AS data_docto,
    MAX(MOV_DT_VENCIMENTO)                    AS data_vencto,
    MAX(MOV_DT_PRORROGADO)                    AS data_prorrogado,
    MAX(MOV_DT_ENTRADA)                       AS data_entrada,
    MAX(TPD_ST_CODIGO)                        AS tpd_codigo,
    MAX(MOV_ST_DOCUMENTO)                     AS documento,
    MAX(MOV_ST_PARCELA)                       AS parcela,
    MAX(CPA_IN_AP)                            AS ap,
    MAX(NVL(MOV_RE_VALOR,          0))        AS valor,
    MAX(NVL(MOV_RE_IR,             0))        AS ret_ir,
    MAX(NVL(MOV_RE_INSS,           0))        AS ret_inss,
    MAX(NVL(MOV_RE_ISS,            0))        AS ret_iss,
    MAX(NVL(MOV_RE_PCC,            0))        AS ret_pcc,
    MAX(NVL(MOV_RE_PIS,            0))        AS ret_pis,
    MAX(NVL(MOV_RE_COFINS,         0))        AS ret_cofins,
    MAX(NVL(MOV_RE_CSLL,           0))        AS ret_csll,
    MAX(NVL(MOV_RE_SEST,           0))        AS ret_sest,
    MAX(NVL(MOV_RE_CAUCAO,         0))        AS ret_caucao,
    MAX(NVL(MOV_RE_FUNRURAL,       0))        AS ret_funrural,
    MAX(NVL(MOV_RE_TOTALRETENCAO,  0))        AS ret_total,
    MAX(NVL(MOV_RE_DESCONTO,       0))        AS desconto,
    MAX(NVL(MOV_RE_ABATIMENTO,     0))        AS abatimento,
    MAX(NVL(MOV_RE_TOTALDESCONTO,  0))        AS total_desconto,
    MAX(NVL(MOV_RE_JUROSMULTA,     0))        AS juros_multa,
    MAX(NVL(MOV_RE_ACRESCIMO,      0))        AS acrescimo,
    MAX(NVL(MOV_RE_TOTALACRESCIMO, 0))        AS total_acrescimo,
    MAX(NVL(MOV_RE_LIQUIDO,        0))        AS liquido,
    MAX(NVL(MOV_RE_ADIANTAMENTO,   0))        AS adiantamento,
    MAX(NVL(MOV_RE_BAIXA,          0))        AS baixa,
    MAX(NVL(MOV_RE_ESTORNO,        0))        AS estorno,
    MAX(NVL(MOV_RE_TOTALBAIXA,     0))        AS total_baixa,
    MAX(NVL(MOV_RE_ABERTO,         0))        AS aberto,
    MAX(NVL(MOV_RE_DEVOLUCAO,      0))        AS devolucao,
    MAX(NVL(MOV_RE_PERMUTA,        0))        AS permuta,
    MAX(NVL(MOV_RE_BAIXAPERMUTA,   0))        AS baixa_permuta,
    MAX(NVL(MOV_RE_BAIXADUPLICATA, 0))        AS baixa_duplicata,
    MAX(NVL(MOV_RE_DEVOLDUPLICATA, 0))        AS devol_duplicata,
    MAX(NVL(MOV_RE_VARCAMBIALPOSITIVA, 0))    AS var_cambial_pos,
    MAX(NVL(MOV_RE_VARCAMBIALNEGATIVA, 0))    AS var_cambial_neg,
    MAX(NVL(MOV_RE_SALDOVARIACAO,  0))        AS saldo_variacao,
    MAX(NVL(MOV_RE_VARMONETARIA,   0))        AS var_monetaria,
    MAX(NVL(MOV_RE_CHEQUEDEVOLVIDO,0))        AS cheque_devolvido,
    MAX(MOV_ST_COMPLHIST)                     AS complemento_hist
FROM MEGA.FIN_FINANCANALITICO@RAC
WHERE MOV_ST_TIPOLINHA = 'Movimento'
GROUP BY MOV_IN_NUMLANCTO
ORDER BY MOV_IN_NUMLANCTO
"""

def main():
    started = time.time()
    print("\n=== sync_fin_analitico ===")
    try:
        print("  Lendo Oracle…")
        rows = fetch_oracle(SQL)
        print(f"  {len(rows)} títulos únicos lidos. Enviando…")
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
