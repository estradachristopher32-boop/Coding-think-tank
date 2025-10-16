"""
Minimal Envelope model used across the agent skeletons.

This is a light approximation to the original Envelope used in tg_bridge.
It supports id/corr, simple JSON (de)serialization, and placeholder sign/verify.
"""
from dataclasses import dataclass, field, asdict
import json, uuid, time
from typing import Any, Dict

@dataclass
class Trace:
    session: str = ""
    path: list = field(default_factory=list)

@dataclass
class Envelope:
    sender: str
    target: str
    kind: str  # "request" or "response" or "error"
    intent: str
    corr: str = None
    payload: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace: Trace = field(default_factory=Trace)
    sig: str = ""

    def __post_init__(self):
        if not self.corr:
            self.corr = self.id
        if not self.trace.session:
            self.trace.session = str(int(time.time()))

    def model_dump_json(self, indent=None):
        return json.dumps(asdict(self), indent=indent)

    def sign(self, secret: str):
        # lightweight placeholder signature
        self.sig = f"sig-{self.id[:8]}"

    def verify(self, secret: str):
        # placeholder: accept if sig present
        return bool(self.sig)

    def expired(self):
        # placeholder: never expire
        return False

    @classmethod
    def parse_obj(cls, obj):
        # accepts dicts from FileQueue
        return cls(**obj)
