"""Entscheidung: rein regelbasiert aus der Finding-Liste, kein LLM beteiligt."""
from __future__ import annotations

from dataclasses import dataclass

from checks.base import Finding

FREIGEBEN = "freigeben"
HINSCHAUEN = "hinschauen"


@dataclass
class Decision:
    status: str
    blocking_reasons: list[Finding]
    info_notes: list[Finding]


def decide(findings: list[Finding]) -> Decision:
    """blocking_reasons = tatsächliche hinschauen-Gründe.
    info_notes = alle übrigen Checks (bestanden oder reines INFO) - für volle
    Nachvollziehbarkeit im Bericht, auch bei freigeben (z.B. um im Gespräch zu
    zeigen, dass D6 knapp innerhalb der Toleranz lag, bevor man die Toleranz live ändert).
    """
    blocking = [f for f in findings if f.blocks]
    non_blocking = [f for f in findings if not f.blocks]
    status = HINSCHAUEN if blocking else FREIGEBEN
    return Decision(status=status, blocking_reasons=blocking, info_notes=non_blocking)
