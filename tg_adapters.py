"""
Agent handlers (cody, brody, quant) — extracted and simplified from tg_bridge.
These handlers return Envelope objects (responses) and do not perform network calls.
"""
import os, datetime
from typing import Dict, Any, List
from tg_schema import Envelope

TG_SHARED_SECRET = os.getenv("TG_SHARED_SECRET", "CHANGE_ME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

def now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def build_request(sender: str, target: str, intent: str, payload: Dict[str,Any]) -> Envelope:
    env = Envelope(sender=sender, target=target, kind="request", intent=intent, payload=payload)
    env.corr = env.id
    env.trace.path.append(sender)
    env.sign(TG_SHARED_SECRET)
    return env

def _mk_needs(needs: List[Dict[str,Any]]):
    return needs

def quant_handle(envelope: Envelope) -> Envelope:
    p = envelope.payload or {}
    needs: List[Dict[str,Any]] = []
    signal = {"t": now_iso(), "type": "watch", "confidence": 0.5, "note": "Local stub."}
    out = Envelope(sender="quant", target=envelope.sender, kind="response",
                   intent="market_analysis_response", corr=envelope.corr,
                   payload={"symbol": p.get("symbol"), "signals": [signal], "explain_md": "Quant stub.", "needs": _mk_needs(needs)})
    out.trace.session = envelope.trace.session
    out.trace.path = envelope.trace.path + ["quant"]
    out.sign(TG_SHARED_SECRET)
    return out

def brody_handle(envelope: Envelope) -> Envelope:
    needs: List[Dict[str,Any]] = []
    # some example intents handled
    if envelope.intent == "ux_spec_request":
        feature = envelope.payload.get("feature","Unnamed")
        spec = {"feature": feature, "pages": [{"route": "/", "components": ["Header","Hero","CTA"]}]}
        out = Envelope(sender="brody", target=envelope.sender, kind="response",
                       intent="ux_spec_response", corr=envelope.corr,
                       payload={"spec": spec, "needs": _mk_needs(needs)})
    elif envelope.intent == "generate_weekly_plan_request":
        p = envelope.payload or {}
        plan = {"summary":{"assumptions": p.get("assumptions", {})}, "meals": {}, "shopping_list": []}
        out = Envelope(sender="brody", target=envelope.sender, kind="response",
                       intent="generate_weekly_plan_response", corr=envelope.corr,
                       payload={"plan": plan, "needs": _mk_needs(needs)})
    else:
        out = Envelope(sender="brody", target=envelope.sender, kind="error",
                       intent="error", corr=envelope.corr, payload={"code":"E_UNSUPPORTED","detail":envelope.intent})
    out.trace.session = envelope.trace.session
    out.trace.path = envelope.trace.path + ["brody"]
    out.sign(TG_SHARED_SECRET)
    return out

def cody_handle(envelope: Envelope) -> Envelope:
    # very small stub for cody (code/comms assistant)
    resp = {"summary": f"Cody handled {envelope.intent}", "example": "# example stub"}
    out = Envelope(sender="cody", target=envelope.sender, kind="response", intent="code_assist_response",
                   corr=envelope.corr, payload={"answer": resp, "needs": _mk_needs([])})
    out.trace.session = envelope.trace.session
    out.trace.path = envelope.trace.path + ["cody"]
    out.sign(TG_SHARED_SECRET)
    return out
