"""
Simple file-queue transport. Writes JSON files into base_dir/queue/<agent>/{in,out}
A minimal RedisStreams stub is included for later wiring.
"""
import pathlib, json, time
from typing import Optional, Tuple

class FileQueue:
    def __init__(self, base_dir: str):
        self.base = pathlib.Path(base_dir)
        for agent in ["cody","quant","brody"]:
            (self.base/"queue"/agent/"in").mkdir(parents=True, exist_ok=True)
            (self.base/"queue"/agent/"out").mkdir(parents=True, exist_ok=True)

    def inbox(self, agent: str) -> pathlib.Path:
        return self.base/"queue"/agent/"in"

    def send(self, target: str, envelope: dict) -> str:
        inbox = self.inbox(target)
        final = inbox/f"{envelope.get('id','msg')}.json"
        with open(final, "w", encoding="utf-8") as f:
            json.dump(envelope, f)
        return str(final)

    def recv(self, agent: str, timeout_sec: float = 0.5) -> Optional[Tuple[str, dict]]:
        inbox = self.base/"queue"/agent/"in"
        # simple poll for the oldest file
        files = sorted(inbox.glob("*.json"), key=lambda p: p.stat().st_mtime)
        if not files:
            time.sleep(timeout_sec)
            return None
        p = files[0]
        with open(p, "r", encoding="utf-8") as f:
            obj = json.load(f)
        try:
            p.unlink()
        except Exception:
            pass
        return (str(p), obj)

# Minimal RedisStreams stub for parity with original code
class RedisStreams:
    def __init__(self, url: str):
        self.url = url
        raise RuntimeError("RedisStreams not implemented in skeleton. Use FileQueue for local testing.")
