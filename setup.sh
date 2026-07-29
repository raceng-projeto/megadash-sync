#!/bin/bash
set -e
cd /opt/megadash-sync

echo "=== 1/3 Baixando Oracle Instant Client 23.4 ==="
if [ ! -d "instantclient" ]; then
  apt-get update -qq
  # Ubuntu 24.04 (noble) renomeou libaio1 -> libaio1t64. Tenta os dois.
  apt-get install -y -qq libaio1t64 unzip wget python3-venv python3-pip \
    || apt-get install -y -qq libaio1 unzip wget python3-venv python3-pip
  wget -q https://download.oracle.com/otn_software/linux/instantclient/2340000/instantclient-basic-linux.x64-23.4.0.24.05.zip -O ic.zip
  unzip -q ic.zip
  mv instantclient_23_4 instantclient
  rm ic.zip
  echo "Instant Client instalado em /opt/megadash-sync/instantclient"
else
  echo "Instant Client já instalado, pulando."
fi

# Garante que libaio.so.1 existe (Ubuntu 24.04 só entrega libaio.so.1t64)
if ! ldconfig -p | grep -q "libaio.so.1 "; then
  AIO_T64=$(ldconfig -p | awk '/libaio.so.1t64/ {print $NF; exit}')
  if [ -n "$AIO_T64" ]; then
    ln -sf "$AIO_T64" /usr/lib/x86_64-linux-gnu/libaio.so.1
    echo "Symlink libaio.so.1 -> $AIO_T64 criado"
  fi
fi

# Registra o instantclient no ldconfig pra resolver libnnz.so, libclntsh.so etc.
echo "/opt/megadash-sync/instantclient" > /etc/ld.so.conf.d/megadash-instantclient.conf
ldconfig

echo "=== 2/3 Criando venv Python ==="
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
./venv/bin/pip install --quiet --upgrade pip
./venv/bin/pip install --quiet oracledb requests

echo "=== 3/3 Testando conexão Oracle ==="
mkdir -p logs
./venv/bin/python -c "
import oracledb
oracledb.init_oracle_client(lib_dir='/opt/megadash-sync/instantclient')
conn = oracledb.connect(user='RAC', password='P9mXf0BE63', dsn='dbconnect.megaerp.online:4221/xepdb1')
cur = conn.cursor()
cur.execute('SELECT 1 FROM dual')
print('OK — Oracle respondeu:', cur.fetchone())
conn.close()
"

echo ""
echo "✅ Setup completo!"
echo ""
echo "Pra ativar o cron horário rode:"
echo '  (crontab -l 2>/dev/null; echo "0 * * * * /opt/megadash-sync/run_all.sh >> /opt/megadash-sync/logs/cron.log 2>&1") | crontab -'