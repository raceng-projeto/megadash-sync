# MegaDash Sync

Sincroniza Oracle MegaERP → Supabase, uma vez por dia.

## Rodando via GitHub Actions (atual — sem servidor)

Workflow em `.github/workflows/daily-sync.yml`, agendado pra `0 3 * * *` (03:00 UTC =
meia-noite BRT). Não precisa de VPS: o runner do GitHub instala o Instant Client e as
deps a cada execução e descarta tudo no final.

### Setup (uma vez)

Em **Settings → Secrets and variables → Actions → New repository secret**, adicionar:

- `ORACLE_USER`
- `ORACLE_PASSWORD`
- `ORACLE_DSN`
- `SUPABASE_URL`
- `SYNC_API_KEY`
- `SUPABASE_ANON_KEY`

(valores iguais aos que estavam no `.env` da VPS)

### Rodar manualmente / ver logs

Aba **Actions → Daily MegaDash Sync → Run workflow** (dispara na hora, sem esperar o
agendamento). Cada execução guarda os logs como artifact por 14 dias.

## Rodando em VPS própria (legado)

```bash
git clone <url-deste-repo> /opt/megadash-sync
cd /opt/megadash-sync
cp .env.example .env && nano .env   # preencher segredos reais
chmod +x setup.sh run_all.sh deploy.sh
./setup.sh
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/megadash-sync/run_all.sh >> /opt/megadash-sync/logs/cron.log 2>&1") | crontab -
```

Deploy: `/opt/megadash-sync/deploy.sh` (`git pull`; `venv/`, `instantclient/`, `logs/`
e `.env` não são versionados e ficam intactos).

## Estrutura

```
├── .github/workflows/daily-sync.yml   # execução agendada (GitHub Actions)
├── setup.sh                           # instala dependências (uso VPS)
├── run_all.sh                         # roda todos os scripts em sequência (uso VPS)
├── deploy.sh                          # git pull (uso VPS)
├── config.py                          # lê segredos de env vars
├── .env.example                       # template de segredos (uso VPS)
├── _common.py                         # helpers: fetch Oracle, POST Supabase, log
├── sync_cadastro_agentes.py
├── sync_cadastro_projetos.py
├── sync_fin_centro_custo.py
├── sync_fin_lancproj.py
├── sync_fin_movimentos.py
├── sync_fin_retencoes.py
└── sync_fin_baixas.py
```
