from lp_core.discovery_kernel import DiscoveryKernel
from lp_core.hypothesis_engine import HypothesisEngine
from lp_core.harvester_kernel import HarvesterKernel
from lp_core.redeemer import Redeemer
from lp_core.governor import Governor
from lp_core.retooler import Retooler
from lp_core.utils import load_json, now_utc, append_jsonl
from lp_core.merkle import merkle_root
import time, os, pathlib

CFG = "configs/lp_config.json"
RED = "configs/lp_redline.json"
LEDGER_DIR = "ledger"
BLOCKS_DIR = "ledger/blocks"
STATE_PATH = "ledger/state.json"

def ensure_dirs():
    pathlib.Path(LEDGER_DIR).mkdir(parents=True, exist_ok=True)
    pathlib.Path(BLOCKS_DIR).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(STATE_PATH):
        append_jsonl(STATE_PATH, {"ts": now_utc(), "state": "init"})

def main():
    ensure_dirs()
    cfg = load_json(CFG)
    red = load_json(RED)

    discover = DiscoveryKernel(cfg, red)
    hypo = HypothesisEngine(cfg, red)
    harvest = HarvesterKernel(cfg, red)
    redeem = Redeemer(cfg, red)
    gov = Governor(cfg, red)
    retool = Retooler(cfg, red)

    loop_delay = cfg.get("loop_delay_seconds", 30)
    block_every = cfg.get("block_every_events", 100)
    events_since_block = 0
    events_path = os.path.join(LEDGER_DIR, "events.jsonl")

    while True:
        if gov.should_safe_exit():
            gov.safe_exit("Governor requested SAFE_EXIT")
            break

        # 1) discovery
        candidates = discover.sample_and_score()
        # 2) hypothesis tests (with placebo)
        validated = []
        for c in candidates:
            res = hypo.test_candidate(c)
            if res.get("pass"):
                validated.append(res)

        # 3) harvest validated
        minted = []
        for v in validated:
            out = harvest.harvest(v)
            if out.get("success"):
                evt = {
                    "ts": now_utc(),
                    "type": "mint",
                    "seed": out["seed"],
                    "meta": out["meta"],
                    "stats": v.get("stats"),
                }
                append_jsonl(events_path, evt)
                minted.append(evt)
                events_since_block += 1

        # 4) redeem / produce intrinsic primitive artifacts
        if minted:
            redeem.update_with_events(minted)

        # 5) governor checks
        gov.observe_tick(minted=minted)
        if gov.trip_redline():
            gov.safe_exit("Redline tripped")
            break

        # 6) retool/probe management
        retool.reallocate(discover, hypo, harvest)

        # 7) block commit
        if events_since_block >= block_every:
            with open(events_path, "rb") as fh:
                # naive pass to compute Merkle over last block_every lines
                # NOTE: in real impl, track a rolling buffer
                pass
            # quick commit of entire file root for simplicity
            root = merkle_root(events_path)
            blk = {
                "ts": now_utc(),
                "merkle_root": root,
                "events": events_since_block
            }
            append_jsonl(os.path.join(BLOCKS_DIR, "blocks.jsonl"), blk)
            events_since_block = 0

        time.sleep(loop_delay)

if __name__ == "__main__":
    main()
