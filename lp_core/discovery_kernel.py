from .utils import now_utc
import requests, random, time

PUBLIC_SOURCES = {
    "ntp_echo": ["http://worldtimeapi.org/api/timezone/Etc/UTC"],
    "dns_echo": ["https://cloudflare-dns.com/dns-query?name=example.com&type=A"],
    "btc_tip":  ["https://blockstream.info/api/blocks/tip/height"],
}

class DiscoveryKernel:
    def __init__(self, cfg, red):
        self.cfg = cfg
        self.red = red
        self.jitter_ms = cfg.get("discovery_jitter_ms", 200)

    def _poll(self, url, kind):
        t0 = time.time()
        try:
            r = requests.get(url, timeout= self.cfg.get("timeout_seconds",10))
            latency = (time.time() - t0)
            status = r.status_code
            body = r.text[:512]
        except Exception as e:
            latency = None
            status = 599
            body = str(e)
        return {"ts": now_utc(), "kind": kind, "url": url, "latency": latency, "status": status, "body": body}

    def sample_and_score(self):
        """Return list of candidate dicts with novelty/delta heuristics.
           Keep it simple: pick a few sources, compute naive deltas."""
        cands = []
        for kind, urls in PUBLIC_SOURCES.items():
            url = random.choice(urls)
            obs = self._poll(url, kind)
            # naive delta: status != 200 or latency > threshold
            delta = 0.0
            if obs["status"] != 200: delta += 1.0
            if isinstance(obs["latency"], (int,float)) and obs["latency"] > 0.8:
                delta += (obs["latency"] - 0.8)
            novelty = delta  # placeholder scoring
            if novelty >= self.cfg.get("novelty_threshold", 0.25):
                cands.append({"obs": obs, "novelty": novelty, "hypothesis": f"{kind}_delta"})
        return cands
