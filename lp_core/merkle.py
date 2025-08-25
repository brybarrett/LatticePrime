from .utils import sha256_str

def merkle_root(file_path: str) -> str:
    # Simple line-based Merkle: hash each line, fold pairwise
    with open(file_path, "r", encoding="utf-8") as f:
        leaves = [sha256_str(line.rstrip("\n")) for line in f if line.strip()]
    if not leaves:
        return sha256_str("EMPTY")
    layer = leaves
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i+1] if i+1 < len(layer) else a
            nxt.append(sha256_str(a + b))
        layer = nxt
    return layer[0]
