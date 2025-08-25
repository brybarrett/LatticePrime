from .utils import load_json, now_utc

class Governor:
    def __init__(self, cfg, red):
        self.cfg = cfg
        self.red = red
        self.errors_recent = 0
        self.minted_recent = 0

    def observe_tick(self, minted):
        self.minted_recent += len(minted)

    def trip_redline(self) -> bool:
        # Simple guard: throttle if too many events per loop
        if self.minted_recent > self.red.get("max_events_per_run", 25):
            return True
        return False

    def should_safe_exit(self) -> bool:
        return False

    def safe_exit(self, reason: str):
        # Write SAFE_EXIT marker
        from .utils import append_jsonl
        append_jsonl("ledger/state.json", {"ts": now_utc(), "state": "SAFE_EXIT", "reason": reason})
