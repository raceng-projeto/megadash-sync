#!/bin/bash
# Roda todos os syncs em sequência. Chamado pelo cron a cada hora.
set -u
cd /opt/megadash-sync
mkdir -p logs

# Segredos (ORACLE_PASSWORD, SYNC_API_KEY, SUPABASE_ANON_KEY, ...) vêm de .env — não versionado
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

STAMP=$(date +%Y%m%d_%H%M%S)
LOG="logs/run_${STAMP}.log"
PY="./venv/bin/python"

echo "=========== MegaDash Sync — $(date) ===========" | tee -a "$LOG"

# Ordem: cadastros primeiro (referências), depois movimentos/analítico
for script in \
    sync_cadastro_agentes.py \
    sync_cadastro_projetos.py \
    sync_fin_movimentos.py \
    sync_fin_lancproj.py \
    sync_fin_centro_custo.py \
    sync_fin_retencoes.py \
    sync_fin_baixas.py
do
    echo "" | tee -a "$LOG"
    echo ">>> $script" | tee -a "$LOG"
    $PY "$script" 2>&1 | tee -a "$LOG" || echo "[!] $script falhou — continuando" | tee -a "$LOG"
done

echo "" | tee -a "$LOG"
echo "=========== Fim — $(date) ===========" | tee -a "$LOG"

# Rotação: mantém apenas os 30 últimos logs
ls -1t logs/run_*.log 2>/dev/null | tail -n +31 | xargs -r rm