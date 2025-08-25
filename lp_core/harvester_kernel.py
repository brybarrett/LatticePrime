from .utils import sha256_str, now_utc

class HarvesterKernel:
    def __init__(self, cfg, red):
        self.cfg = cfg
        self.red = red

    def harvest(self, validated: dict):
        # Convert candidate delta into a whitened+hashed seed (placeholder)
        payload = f"{validated['candidate']['hypothesis']}|{validated['candidate']['obs']['status']}|{validated['candidate']['obs']['latency']}|{now_utc()}"
        seed = sha256_str(payload)
        meta = {
            "kind": validated["candidate"]["obs"]["kind"],
            "url": validated["candidate"]["obs"]["url"],
            "novelty": validated["candidate"]["novelty"]
        }
        return {"success": True, "seed": seed, "meta": meta}
