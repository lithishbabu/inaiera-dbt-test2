"""Python job: READ-ONLY check of what the Runner's job environment can do. It changes nothing and always ends with exit code 0, so the
run shows 'succeeded' and the whole printout stays readable in the run output.

It answers, from INSIDE the Runner: when did the job really start; where does it run; which integration settings does the Runner pass
(names and presence only, never secret values); can it reach Trino, the Catalog (lineage URL), GitHub and the Azure storage; and is
there room to write. Packages: only the standard library, plus `trino` (already in requirements.txt) for the one Trino check.
"""
import os
import platform
import shutil
import socket
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

T0 = time.time()
print(f"1. START  {datetime.now(timezone.utc).isoformat(timespec='seconds')}  (compare with the time you clicked Run now)")
print(f"   host/pod: {socket.gethostname()}   python {platform.python_version()}   cwd: {os.getcwd()}")
print(f"   inside Kubernetes: {'yes' if os.environ.get('KUBERNETES_SERVICE_HOST') else 'no'}\n")

# 2. Which integration settings did the Runner hand to this job? Names + whether set. Values only for harmless ones.
print("2. SETTINGS the job can see (names and whether they are set; secrets are never printed)")
PREFIXES = ("INAIERA_", "OPENLINEAGE", "UCS_", "DAGSTER", "AZURE", "ARTIFACT", "TRINO", "CLICKHOUSE", "DBT_", "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY")
SHOW_VALUE = {"INAIERA_TRINO_HOST", "INAIERA_TRINO_PORT", "INAIERA_TRINO_HTTP_SCHEME", "INAIERA_TRINO_CATALOG", "INAIERA_TRINO_USER"}
for k in sorted(os.environ):
    if k.upper().startswith(PREFIXES):
        v = os.environ[k]
        if k in SHOW_VALUE:
            shown = v
        elif k.upper().endswith(("URL", "URI", "ENDPOINT")) and v:
            p = urlparse(v)
            shown = f"{p.scheme}://{p.hostname}{':' + str(p.port) if p.port else ''}{p.path}"      # no user/password, no query
        else:
            shown = "set" if v else "EMPTY"
        print(f"   {k:<34} {shown}")
for k in ("OPENLINEAGE_URL", "UCS_INTERNAL_TOKEN"):
    if not os.environ.get(k):
        print(f"   {k:<34} NOT SET in this job's environment (the dbt Runner's own setting may still exist; this is only what the job sees)")
print()


def tcp(label, host, port, timeout=6):
    t = time.time()
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            print(f"   OK    {label:<26} {host}:{port}  connected in {time.time() - t:.2f}s")
            return True
    except Exception as e:  # noqa: BLE001
        print(f"   FAIL  {label:<26} {host}:{port}  after {time.time() - t:.2f}s  {type(e).__name__}: {str(e)[:120]}")
        return False


def http_status(label, url, timeout=8):
    """One GET with no credentials: any HTTP answer (even 401/404/405) proves the address is reachable. Nothing is sent but the GET."""
    t = time.time()
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "runner-diagnose"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception as e:  # noqa: BLE001
        print(f"   FAIL  {label:<26} {url}  after {time.time() - t:.2f}s  {type(e).__name__}: {str(e)[:120]}")
        return
    print(f"   OK    {label:<26} {url}  answered HTTP {code} in {time.time() - t:.2f}s")


print("3. REACHABILITY from the job")
if os.environ.get("INAIERA_TRINO_HOST"):
    tcp("Trino", os.environ["INAIERA_TRINO_HOST"], os.environ.get("INAIERA_TRINO_PORT", "8080"))
ol = os.environ.get("OPENLINEAGE_URL")
if ol:
    p = urlparse(ol)
    tcp("Catalog (lineage URL)", p.hostname, p.port or (443 if p.scheme == "https" else 80))
    http_status("Catalog HTTP", f"{p.scheme}://{p.hostname}{':' + str(p.port) if p.port else ''}/")
tcp("GitHub", "github.com", 443)
acct = os.environ.get("AZURE_STORAGE_ACCOUNT") or os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
if acct:
    tcp("Azure blob storage", f"{acct}.blob.core.windows.net", 443)
print()

print("4. TRINO  select 1  (proves the job's Trino connection works and how fast it answers)")
try:
    import trino
    jwt = os.environ.get("INAIERA_TRINO_JWT")
    t = time.time()
    conn = trino.dbapi.connect(
        host=os.environ["INAIERA_TRINO_HOST"], port=int(os.environ["INAIERA_TRINO_PORT"]),
        http_scheme=os.environ["INAIERA_TRINO_HTTP_SCHEME"], catalog=os.environ.get("INAIERA_TRINO_CATALOG", ""),
        user=os.environ.get("INAIERA_TRINO_USER", "inaiera-python-job"),
        auth=trino.auth.JWTAuthentication(jwt) if jwt else None,
    )
    cur = conn.cursor()
    cur.execute("select 1")
    print(f"   OK    answered {cur.fetchall()} in {time.time() - t:.2f}s")
except Exception as e:  # noqa: BLE001
    print(f"   FAIL  {type(e).__name__}: {str(e)[:300]}")
print()

print("5. DISK  (a job that cannot write or has no space fails before it starts)")
for d in ("/tmp", os.getcwd()):
    try:
        u = shutil.disk_usage(d)
        probe = os.path.join(d, ".diagnose_probe")
        with open(probe, "w") as f:
            f.write("x")
        os.remove(probe)
        print(f"   OK    {d:<14} writable, {u.free / 1e9:.1f} GB free of {u.total / 1e9:.1f} GB")
    except Exception as e:  # noqa: BLE001
        print(f"   FAIL  {d:<14} {type(e).__name__}: {str(e)[:120]}")
print()

print(f"6. DONE  this script ran for {time.time() - T0:.1f}s; the job's start time above, minus the time you clicked Run now, is how long the hand-over took.")
sys.exit(0)
