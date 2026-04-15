from __future__ import annotations

import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class RunContext:
    run_id: str = field(default_factory=lambda: str(uuid4()))
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    stage_counts: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {"in": 0, "out": 0, "excluded": 0}))
    exclusions: list[dict] = field(default_factory=list)
    fallbacks: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def record_stage(self, stage: str, in_count: int, out_count: int, excluded_count: int = 0) -> None:
        self.stage_counts[stage] = {"in": in_count, "out": out_count, "excluded": excluded_count}

    def add_exclusion(self, deal_id: str, stage: str, reason: str) -> None:
        self.exclusions.append({"deal_id": deal_id, "stage": stage, "reason": reason})

    def add_fallback(self, deal_id: str, module: str, source: str, reason: str) -> None:
        self.fallbacks.append({"deal_id": deal_id, "module": module, "source": source, "reason": reason})

    def fallback_counts(self) -> dict[str, int]:
        c = Counter([f["module"] for f in self.fallbacks])
        return dict(c)


def git_commit_hash() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None
