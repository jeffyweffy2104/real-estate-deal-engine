from __future__ import annotations

import math
from typing import Iterable


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 3959.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return r * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def median(values: list[float]) -> float:
    s = sorted(values)
    n = len(s)
    if n == 0:
        raise ValueError("median of empty list")
    m = n // 2
    return s[m] if n % 2 == 1 else (s[m - 1] + s[m]) / 2


def trimmed(values: list[float], trim_ratio: float = 0.1) -> list[float]:
    if len(values) < 5:
        return sorted(values)
    s = sorted(values)
    cut = max(1, int(len(s) * trim_ratio))
    if len(s) <= cut * 2:
        return s
    return s[cut:-cut]


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def safe_mean(values: Iterable[float]) -> float:
    vals = list(values)
    return sum(vals) / len(vals) if vals else 0.0
