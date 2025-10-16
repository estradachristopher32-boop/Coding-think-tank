# Agent Think Tank (Coding-think-tank)

This repository contains extracted agent skeletons (Cody, Brody, Quant) and runner/transport tooling pulled from tg_bridge. It is a copy-only import intended as a lightweight starting point for developing multi-agent think-tanks and local runners. The code is intentionally minimal to make it easy to iterate on.

Quick start

1. Create a virtual environment and install dependencies:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

2. Run a brody worker (file-queue transport):
   python tg_worker_brody.py

3. From another shell, send a request using tg_hub.py:
   python tg_hub.py request --target brody --intent ux_spec_request --payload '{"feature":"Example"}'

Notes
- brody_generate.py imports tg_adapters; the adapters and schema are included in this repo as minimal working skeletons.
