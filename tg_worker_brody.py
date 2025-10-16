#!/usr/bin/env python3
"""
File-queue worker loop for brody. Reads from queue, verifies Envelope, runs handler and writes response.
"""
import time, json, os
from dotenv import load_dotenv
from tg_transport import FileQueue, RedisStreams
from tg_schema import Envelope
from tg_adapters import TG_SHARED_SECRET, brody_handle

load_dotenv()

TRANSPORT = os.getenv("TG_TRANSPORT", "file")
BASE_DIR = os.getenv("TG_BASE_DIR", os.getcwd())
REDIS_URL = os.getenv("REDIS_URL", "")

if TRANSPORT.lower() == "redis":
    tx = RedisStreams(REDIS_URL)
    last_id = "0-0"
    print("[brody] worker online (redis)")
else:
    tx = FileQueue(BASE_DIR)
    print("[brody] worker online (file-queue)")

while True:
    if TRANSPORT.lower() == "redis":
        # Not implemented in stub
        time.sleep(0.5)
        continue
    else:
        r = tx.recv("brody")
        if not r:
            time.sleep(0.2)
            continue
        _path, obj = r
        env = Envelope.parse_obj(obj)

    if env.expired():
        continue
    if not env.verify(TG_SHARED_SECRET):
        continue

    out = brody_handle(env)
    tx.send(out.target, json.loads(out.model_dump_json()))
