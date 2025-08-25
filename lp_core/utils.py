import orjson, time, hashlib, os

def now_utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def load_json(path):
    with open(path, "rb") as f:
        return orjson.loads(f.read())

def save_json(path, obj):
    with open(path, "wb") as f:
        f.write(orjson.dumps(obj))

def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "ab") as f:
        f.write(orjson.dumps(obj))
        f.write(b"\n")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_str(s: str) -> str:
    return sha256_bytes(s.encode("utf-8"))
