#!/usr/bin/env python3
"""
tg_hub: send a request to an agent and wait for a response via FileQueue.
"""
import argparse, json, os, time
from dotenv import load_dotenv
from tg_schema import Envelope
from tg_transport import FileQueue, RedisStreams
from tg_adapters import TG_SHARED_SECRET, build_request

load_dotenv()

TRANSPORT = os.getenv("TG_TRANSPORT","file")
BASE_DIR = os.getenv("TG_BASE_DIR", os.getcwd())
REDIS_URL = os.getenv("REDIS_URL","")

if TRANSPORT.lower() == "redis":
    tx = RedisStreams(REDIS_URL)
else:
    tx = FileQueue(BASE_DIR)

def send_and_wait(env: Envelope, timeout_sec=15):
    path_or_id = tx.send(env.target, json.loads(env.model_dump_json()))
    print(f"sent -> {env.target}: {path_or_id}")

    start = time.time()
    while time.time() - start < timeout_sec:
        r = tx.recv(env.sender)
        if not r:
            time.sleep(0.2); continue
        _path, obj = r
        try:
            env2 = Envelope.parse_obj(obj)
        except Exception:
            continue
        if env2.corr == env.corr and env2.kind in ("response","error"):
            if not env2.verify(TG_SHARED_SECRET):
                raise SystemExit("signature verification failed on response")
            return env2
    raise SystemExit("timeout waiting for response")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sreq = sub.add_parser("request", help="Send a request to an agent")
    sreq.add_argument("--target", required=True, choices=["quant","brody","cody"], help="Agent target")
    sreq.add_argument("--intent", required=True, help="Intent name")
    sreq.add_argument("--payload", default="{}", help="JSON payload string")
    args = ap.parse_args()
    if args.cmd == "request":
        payload = json.loads(args.payload)
        env = build_request("cody", args.target, args.intent, payload)
        resp = send_and_wait(env)
        print("\n=== RESPONSE ===")
        print(resp.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
