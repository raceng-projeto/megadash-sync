#!/bin/bash
# Atualiza o código em produção a partir do git. venv/, instantclient/, logs/ e .env
# ficam fora do git e não são tocados.
set -euo pipefail
cd /opt/megadash-sync
git pull
echo "Deploy OK."
