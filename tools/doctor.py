#!/usr/bin/env python3
"""Read-only presence check. Never print tokens or install dependencies."""
import importlib.util
import json
import os
import platform
from pathlib import Path
import shutil
import sys

result = {
    'python': platform.python_version(),
    'python_at_least_3_10': sys.version_info >= (3, 10),
    'commands_present': {x: bool(shutil.which(x)) for x in
        ('codex', 'git', 'gh', 'node', 'npm', 'docker', 'agent-browser', 'chromium', 'google-chrome')},
    'python_playwright_present': importlib.util.find_spec('playwright') is not None,
    'skill_locations': {
        'modern_user': str(Path.home() / '.agents/skills/product-sprint'),
        'legacy_user': str(Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills/product-sprint')},
    'limits': ['Presence is not login, permission, runtime, or policy validation.',
               'Do not install dependencies or change Codex automatically.',
               'A VS Code-only installation may work even if codex is not on PATH.']
}
print(json.dumps(result, ensure_ascii=False, indent=2))
