#!/usr/bin/env python3
"""Offline, explicit, non-destructive installer for one Codex skill."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from kitlib import ROOT, KitError, verified_files, skill_payload, destination, install_payload

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scope", choices=["project", "user"], required=True)
    p.add_argument("--project", help="Existing allowed project directory")
    p.add_argument("--layout", choices=["modern", "legacy"], default="modern")
    p.add_argument("--apply", action="store_true", help="Without this flag, only preview")
    a = p.parse_args()
    try:
        files = verified_files()
        target = destination(a.scope, a.layout, a.project)
        # Do not turn the public preparation kit into a task workspace.
        if ROOT == target or ROOT in target.parents:
            raise KitError("Install into a separate project or user scope, not the public kit")
        state = install_payload(skill_payload(files), target, a.apply)
        print(json.dumps({"status": state, "path": str(target),
            "network_used": False, "global_instructions_changed": False,
            "codex_updated": False,
            "next": "Confirm product-sprint in Codex skill list; restart only if not visible. File copy is not proof of model recognition."}, ensure_ascii=False, indent=2))
        return 0
    except (KitError, OSError) as exc:
        print("STOP: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
