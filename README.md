# MegaDash Sync

Sincroniza Oracle MegaERP → Supabase a cada hora. Roda isolado em `/opt/megadash-sync/`
na VPS — não toca em nada mais que roda na máquina (cemaden_proxy.py, ifc_scripts, etc.).

## Instalação (primeira vez, como root)

```bash
git clone <url-deste-repo> /opt/megadash-sync
cd /opt/megadash-sync
cp .env.example .env && nano .env   # preencher segredos reais
chmod +x setup.sh run_all.sh deploy.sh
./setup.sh
```

O `setup.sh` instala:
- Oracle Instant Client 23.4 em `/opt/megadash-sync/instantclient` (não mexe em `/opt/oracle`)
- venv Python em `/opt/megadash-sync/venv` com `oracledb` + `requests`

## Ativar cron horário

```bash
(crontab -l 2>/dev/null; echo "0 * * * * /opt/megadash-sync/run_all.sh >> /opt/megadash-sync/logs/cron.log 2>&1") | crontab -
```

## Deploy de atualizações

```bash
/opt/megadash-sync/deploy.sh
```

Só dá `git pull` — `venv/`, `instantclient/`, `logs/` e `.env` não são versionados e ficam intactos.

## Testar manualmente

```bash
/opt/megadash-sync/run_all.sh
tail -f /opt/megadash-sync/logs/cron.log
```

## Segredos

Ficam em `.env` (não versionado, veja `.env.example` pro formato). `run_all.sh` carrega
automaticamente antes de rodar os scripts. Pra rodar um script isolado manualmente:

```bash
set -a; source .env; set +a
./venv/bin/python sync_fin_movimentos.py
```

## Estrutura

```
/opt/megadash-sync/
├── setup.sh                       # instala dependências
├── run_all.sh                     # roda todos os scripts em sequência (chamado pelo cron)
├── deploy.sh                      # git pull
├── config.py                      # lê segredos de env vars
├── .env.example                   # template de segredos
├── _common.py                     # helpers: fetch Oracle, POST Supabase, log
├── sync_cadastro_agentes.py
├── sync_cadastro_projetos.py
├── sync_fin_centro_custo.py
├── sync_fin_lancproj.py
├── sync_fin_movimentos.py
├── instantclient/                 # criado pelo setup, fora do git
├── venv/                          # criado pelo setup, fora do git
└── logs/                          # fora do git
```
