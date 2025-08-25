from .utils import append_jsonl, now_utc

class Redeemer:
    def __init__(self, cfg, red):
        self.cfg = cfg
        self.red = red
        self.beacon_path = "ledger/beacon.jsonl"

    def update_with_events(self, events):
        # Publish a simple randomness/ordering beacon stream (intrinsic utility)
        for e in events:
            append_jsonl(self.beacon_path, {
                "ts": now_utc(),
                "seed": e["seed"],
                "ordering": hash(e["seed"]) & 0xffffffff
            })
