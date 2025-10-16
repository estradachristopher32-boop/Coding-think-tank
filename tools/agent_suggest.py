#!/usr/bin/env python3
"""
Query agents (quant, brody, cody) for suggested materials and write YAML reports.
"""
import argparse, os, time, json, yaml
from tg_adapters import build_request, quant_handle, brody_handle
from tg_schema import Envelope
from tg_transport import FileQueue

def send_and_wait_via_fq(target, req, timeout=8.0):
    fq = FileQueue(os.getcwd())
    try:
        fq.send(target, req.__dict__ if hasattr(req, '__dict__') else json.loads(req.model_dump_json()))
    except Exception:
        fq.send(target, json.loads(req.model_dump_json()))
    start = time.time()
    while time.time() - start < timeout:
        r = fq.recv('market-navigator')
        if not r:
            time.sleep(0.2); continue
        _p, obj = r
        try:
            env = Envelope.parse_obj(obj)
        except Exception:
            continue
        if env.corr == req.corr:
            return env
    return None

def query_agent(agent, context):
    req = build_request('tool', agent, 'materials_suggestion_request', {'context': context})
    if agent == 'quant':
        try:
            resp = quant_handle(req)
            return resp.payload
        except Exception:
            env = send_and_wait_via_fq('quant', req)
            return env.payload if env else {'error':'no reply'}
    if agent == 'brody':
        try:
            resp = brody_handle(req)
            return resp.payload
        except Exception:
            env = send_and_wait_via_fq('brody', req)
            return env.payload if env else {'error':'no reply'}
    env = send_and_wait_via_fq(agent, req)
    if not env:
        return {'error':'no reply'}
    return env.payload

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--agents', default='quant,brody,cody')
    ap.add_argument('--context', default='Suggested training materials for market/ux/agents')
    ap.add_argument('--out', default='bootstrap/agent_suggestions')
    args = ap.parse_args()
    agents = [a.strip() for a in args.agents.split(',') if a.strip()]
    os.makedirs(args.out, exist_ok=True)
    report = {'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'agents':{}}
    for a in agents:
        print(f"Querying {a}...")
        payload = query_agent(a, args.context)
        report['agents'][a] = payload
        fname = os.path.join(args.out, f"{a}_suggestions.yaml")
        with open(fname, 'w', encoding='utf-8') as f:
            yaml.safe_dump({a: payload}, f, sort_keys=False)
        print(f"Wrote {fname}")
    with open(os.path.join(args.out, 'combined.yaml'), 'w', encoding='utf-8') as f:
        yaml.safe_dump(report, f, sort_keys=False)
    print('Done. Reports in', args.out)

if __name__ == '__main__':
    main()
