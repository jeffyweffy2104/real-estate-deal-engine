from __future__ import annotations

import json
import os

from src.data.schemas import RunManifest


def build_manifest(stub: dict, output_files: dict[str, str]) -> RunManifest:
    return RunManifest(**stub, output_files=output_files)


def export_manifest(manifest: RunManifest, output_dir: str, filename: str = "manifest.json") -> str:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest.model_dump(mode="json"), f, sort_keys=True, indent=2)
    return path
