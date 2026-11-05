#!/usr/bin/env python3
"""Publish only verified kit files as a NEW public repository. Personal PC only."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from kitlib import KitError, ROOT, verified_files, validate_rel, no_symlinks

OWNER = re.compile(r'^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$')
NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$')

def checked_identity(owner: str, name: str) -> str:
    if not OWNER.fullmatch(owner) or not NAME.fullmatch(name) or name in ('.', '..'):
        raise KitError('Invalid GitHub owner or repository name')
    return owner + '/' + name

def make_snapshot(files: dict[str, bytes], out: Path) -> None:
    """Copy only the immutable, verified bytes, never the current worktree/history."""
    no_symlinks(out)
    for rel in files:
        validate_rel(rel)
    if out.exists() and any(out.iterdir()):
        raise KitError('Snapshot target must be empty')
    out.mkdir(parents=True, exist_ok=True)
    for rel, data in files.items():
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

def run(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    for key in list(env):
        if key.startswith('GIT_'):
            env.pop(key, None)
    env['GIT_TERMINAL_PROMPT'] = '0'
    env['GH_PROMPT_DISABLED'] = '1'
    # Pin the intended host, without printing or reading credentials.
    env['GH_HOST'] = 'github.com'
    try:
        r = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True,
                           encoding='utf-8', errors='replace', timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise KitError('Command failed or timed out: ' + ' '.join(args[:3])) from exc
    if check and r.returncode:
        # Avoid forwarding arbitrary authentication/remote diagnostics to public logs.
        raise KitError('Command failed: ' + ' '.join(args[:3]) + '. Inspect locally; do not share credentials.')
    return r

def publish(owner: str, name: str, apply: bool = False, root: Path = ROOT) -> dict:
    full = checked_identity(owner, name)
    files = verified_files(root)
    preview = {'status': 'preview', 'repository': full, 'visibility': 'public',
               'files': sorted(files), 'existing_repositories_modified': False,
               'source_git_history_uploaded': False}
    if not apply:
        return preview
    if not shutil.which('gh') or not shutil.which('git'):
        raise KitError('Git and GitHub CLI are required on your personal PC. Nothing installed automatically.')
    who = run(['gh', 'api', 'user', '--jq', '.login']).stdout.strip()
    if who.casefold() != owner.casefold():
        raise KitError('Authenticated personal account does not match requested owner; nothing published')
    existing = run(['gh', 'api', 'repos/' + full, '--include'], check=False)
    if existing.returncode == 0:
        raise KitError('Repository already exists; never overwrite or change its visibility automatically')
    if '404' not in existing.stdout + existing.stderr:
        raise KitError('Could not establish that repository is absent; stopping')
    stage = Path(tempfile.mkdtemp(prefix='product-sprint-publish-'))
    repo = stage / 'snapshot'
    created_attempted = False
    try:
        make_snapshot(files, repo)
        run(['git', 'init', '-b', 'main'], repo)
        run(['git', 'config', 'user.name', owner], repo)
        run(['git', 'config', 'user.email', owner + '@users.noreply.github.com'], repo)
        run(['git', 'config', 'commit.gpgsign', 'false'], repo)
        (stage / 'empty-hooks').mkdir()
        run(['git', 'config', 'core.hooksPath', str(stage / 'empty-hooks')], repo)
        # This credential helper is local to the temporary preparation repository.
        run(['git', 'config', 'credential.https://github.com.helper', '!gh auth git-credential'], repo)
        run(['git', 'add', '--all'], repo)
        run(['git', 'commit', '-m', 'Add verified generic product sprint skill kit'], repo)
        sha = run(['git', 'rev-parse', 'HEAD'], repo).stdout.strip()
        created_attempted = True
        run(['gh', 'repo', 'create', full, '--public', '--description',
             'Generic Codex product sprint skill: decisions, task-first UI, independent review, verified release.',
             '--source', str(repo), '--remote', 'origin', '--push'], repo)
        info = json.loads(run(['gh', 'api', 'repos/' + full]).stdout)
        if info.get('private') is not False:
            raise KitError('Remote public visibility not verified')
        remote = json.loads(run(['gh', 'api', 'repos/' + full + '/git/trees/' + sha + '?recursive=1']).stdout)
        if remote.get('truncated'):
            raise KitError('Remote tree verification was truncated')
        paths = {e['path'] for e in remote.get('tree', []) if e.get('type') == 'blob'}
        if paths != set(files):
            raise KitError('Remote file set did not match the reviewed manifest')
        folder = 'https://github.com/' + full + '/tree/' + sha + '/skills/product-sprint'
        return {'status': 'published-and-verified', 'url': 'https://github.com/' + full,
                'commit': sha, 'public': True, 'file_count': len(paths),
                'codex_message': '$skill-installer ' + folder + ' 의 스킬을 설치하십시오. Codex와 보안 설정은 변경하지 마십시오.',
                'next_message': '$product-sprint 현재 과제 안내를 읽고 시작하십시오.'}
    except Exception as exc:
        if created_attempted:
            raise KitError('Publication was attempted, but full success is NOT verified. Inspect the new remote before retrying. No automatic deletion or overwrite. ' + str(exc)) from exc
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owner', required=True)
    p.add_argument('--name', default='codex-product-sprint-kit')
    p.add_argument('--apply', action='store_true')
    a = p.parse_args()
    try:
        print(json.dumps(publish(a.owner, a.name, a.apply), ensure_ascii=False, indent=2))
        return 0
    except (KitError, OSError, ValueError) as exc:
        print('STOP: ' + str(exc), file=sys.stderr)
        return 2
if __name__ == '__main__':
    raise SystemExit(main())
