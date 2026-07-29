"""Helpers compartilhados pelos scripts de sync."""
import sys
import time
import json
import datetime
import oracledb
import requests
from config import (
    ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, INSTANT_CLIENT_DIR,
    SUPABASE_URL, SYNC_API_KEY, CHUNK_SIZE, HTTP_TIMEOUT,
)

_initialized = False


def init_oracle():
    global _initialized
    if not _initialized:
        oracledb.init_oracle_client(lib_dir=INSTANT_CLIENT_DIR)
        _initialized = True


def get_oracle_conn():
    """Conecta no Oracle com retry — o listener (XE) às vezes recusa conexão
    (ORA-12516/ORA-12520) quando várias conexões chegam ao mesmo tempo."""
    init_oracle()
    for attempt in range(4):
        try:
            conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
            conn.call_timeout = 300_000  # 5min por chamada — evita travar pra sempre numa query presa
            return conn
        except oracledb.DatabaseError as e:
            code = e.args[0].code if e.args and hasattr(e.args[0], "code") else None
            if code in (12516, 12520) and attempt < 3:
                wait = 5 * (attempt + 1)
                print(f"  [!] Oracle recusou conexão (ORA-{code}), tentando de novo em {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            raise


def fetch_oracle(sql: str) -> list[dict]:
    """Executa query no Oracle e retorna lista de dicts (snake_case keys)."""
    conn = get_oracle_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        cols = [c[0].lower() for c in cur.description]
        rows = []
        for r in cur.fetchall():
            d = {}
            for k, v in zip(cols, r):
                if isinstance(v, datetime.datetime):
                    v = v.isoformat()
                elif isinstance(v, datetime.date):
                    v = v.isoformat()
                d[k] = v
            rows.append(d)
        return rows
    finally:
        conn.close()


def post_chunks(endpoint: str, records: list[dict]) -> int:
    """POST em chunks para a edge function. Primeiro chunk apaga (append=false), demais appendem."""
    url = f"{SUPABASE_URL}/functions/v1/{endpoint}"
    headers = {"Content-Type": "application/json", "x-sync-key": SYNC_API_KEY}
    total = 0
    if not records:
        # Mesmo sem registros, dispara um POST vazio? Não — só loga.
        return 0
    for i in range(0, len(records), CHUNK_SIZE):
        chunk = records[i:i + CHUNK_SIZE]
        append = i > 0
        body = json.dumps({"data": chunk, "append": append}, default=str)
        for attempt in range(3):
            try:
                r = requests.post(url, data=body, headers=headers, timeout=HTTP_TIMEOUT)
                if r.status_code == 200:
                    total += len(chunk)
                    print(f"  chunk {i//CHUNK_SIZE+1}: {len(chunk)} OK (append={append})")
                    break
                else:
                    print(f"  chunk {i//CHUNK_SIZE+1} HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
                    if attempt < 2:
                        time.sleep(5)
                    else:
                        raise RuntimeError(f"Falha definitiva no chunk {i//CHUNK_SIZE+1}")
            except requests.RequestException as e:
                print(f"  chunk {i//CHUNK_SIZE+1} erro de rede: {e}", file=sys.stderr)
                if attempt < 2:
                    time.sleep(5)
                else:
                    raise
    return total


def log_sync(table_name: str, records_count: int, status: str = "success", error_message: str | None = None):
    """Registra na tabela sync_log via edge function dedicada."""
    url = f"{SUPABASE_URL}/functions/v1/log-sync"
    headers = {"Content-Type": "application/json", "x-sync-key": SYNC_API_KEY}
    body = {"table_name": table_name, "records_count": records_count, "status": status}
    if error_message:
        body["error_message"] = error_message[:500]
    try:
        requests.post(url, json=body, headers=headers, timeout=30)
    except Exception as e:
        print(f"[warn] log_sync falhou: {e}", file=sys.stderr)


def commit_swap(table: str) -> None:
    """Promove staging -> main de forma atomica via RPC commit_sync_swap."""
    from config import SUPABASE_ANON_KEY
    url = f"{SUPABASE_URL}/rest/v1/rpc/commit_sync_swap"
    headers = {
        "Content-Type": "application/json",
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    }
    r = requests.post(url, json={"p_table": table}, headers=headers, timeout=HTTP_TIMEOUT)
    if r.status_code != 200:
        raise RuntimeError(f"commit_sync_swap {table} HTTP {r.status_code}: {r.text[:300]}")
    print(f"  swap OK: {r.text[:200]}")


def run_sync(table_name: str, endpoint: str, sql: str):
    """Wrapper: executa fetch + post + log com tratamento de erro padronizado."""
    started = time.time()
    print(f"\n=== {table_name} ===")
    try:
        print("  Lendo Oracle...")
        records = fetch_oracle(sql)
        print(f"  {len(records)} registros lidos. Enviando...")
        total = post_chunks(endpoint, records)
        elapsed = time.time() - started
        print(f"  ✅ {total} inseridos em {elapsed:.1f}s")
        log_sync(table_name, total, "success")
    except Exception as e:
        elapsed = time.time() - started
        print(f"  ❌ ERRO após {elapsed:.1f}s: {e}", file=sys.stderr)
        log_sync(table_name, 0, "error", str(e))
        raise