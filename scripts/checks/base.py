from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Finding:
    check_id: str
    level: str  # "BLOCK" | "INFO"
    passed: bool
    message: str
    policy_tunable: bool = False

    @property
    def blocks(self) -> bool:
        return self.level == "BLOCK" and not self.passed


def ok(check_id: str, message: str, level: str = "BLOCK", policy_tunable: bool = False) -> Finding:
    return Finding(check_id=check_id, level=level, passed=True, message=message, policy_tunable=policy_tunable)


def fail(check_id: str, message: str, level: str = "BLOCK", policy_tunable: bool = False) -> Finding:
    return Finding(check_id=check_id, level=level, passed=False, message=message, policy_tunable=policy_tunable)
