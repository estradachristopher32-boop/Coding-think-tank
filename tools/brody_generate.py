#!/usr/bin/env python3
"""
Generate docs/jacob_plan.json by calling brody_handle. This version falls back to a sample
if tg_adapters is not available or if run standalone.
"""
import json, os, sys, pathlib
ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from tg_adapters import build_request, brody_handle
except Exception:
    build_request = None
    brody_handle = None

def sample_plan():
    return {"summary":{"assumptions":{}}, "meals":[], "shopping_list":[]}

def main():
    payload = {"goal": os.getenv('JACOB_GOAL','bulk'),
               "stores": [s for s in (os.getenv('JACOB_STORES') or 'Costco,HEB,Walmart').split(',')],
               "assumptions": {"sex":"male","height_cm":183}}
    if brody_handle is None:
        plan = sample_plan()
    else:
        req = build_request(sender='runner', target='brody', intent='generate_weekly_plan_request', payload=payload)
        resp = brody_handle(req)
        plan = resp.payload.get('plan') if resp and resp.payload else sample_plan()
    out_path = os.path.join('docs','jacob_plan.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path,'w',encoding='utf-8') as f:
        json.dump(plan, f, indent=2)
    print('Wrote', out_path)

if __name__ == '__main__':
    main()
