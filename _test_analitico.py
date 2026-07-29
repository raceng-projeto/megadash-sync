from _common import fetch_oracle

sql = """
SELECT MOV_IN_NUMLANCTO AS num_lancto,
       MAX(AGN_ST_FANTASIA) AS agente,
       MAX(MOV_DT_VENCIMENTO) AS data_vencto,
       MAX(MOV_RE_VALOR) AS valor,
       MAX(NVL(MOV_RE_IR,0)) AS ret_ir,
       MAX(NVL(MOV_RE_ISS,0)) AS ret_iss,
       MAX(NVL(MOV_RE_TOTALRETENCAO,0)) AS ret_total,
       MAX(NVL(MOV_RE_TOTALBAIXA,0)) AS total_baixa,
       MAX(NVL(MOV_RE_ABERTO,0)) AS aberto,
       MAX(CPA_IN_AP) AS ap
FROM MEGA.FIN_FINANCANALITICO@RAC
WHERE MOV_ST_TIPOLINHA = 'Movimento'
  AND (MOV_RE_IR > 0 OR MOV_RE_ISS > 0)
  AND ROWNUM <= 5
GROUP BY MOV_IN_NUMLANCTO
"""

rows = fetch_oracle(sql)
print(f"Analitico: {len(rows)} linhas")
for r in rows:
    print(" ", r)

sql2 = """
SELECT MOV_IN_NUMLANCTO AS num_lancto,
       REF_ST_TIPO AS tipo,
       MAX(REF_ST_DESCRICAO) AS descricao,
       MOV_DT_DATADOCTOBX AS data_baixa,
       MAX(NVL(MOV_RE_VALORBX,0)) AS valor,
       MAX(AGN_ST_FANTASIACTA) AS conta
FROM MEGA.FIN_FINANCANALITICOBX@RAC
WHERE ROWNUM <= 3
GROUP BY MOV_IN_NUMLANCTO, REF_ST_TIPO, MOV_DT_DATADOCTOBX
"""

rows2 = fetch_oracle(sql2)
print(f"Baixas: {len(rows2)} linhas")
for r in rows2:
    print(" ", r)
