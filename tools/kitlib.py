"""Shared, standard-library-only integrity and installation helpers."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKILL_PREFIX = "skills/product-sprint/"
SKILL_NAME = "product-sprint"

class KitError(RuntimeError):
    """A safe stop: no automatic destructive recovery."""

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def validate_rel(name: str) -> str:
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise KitError("Unsafe manifest path")
    p = PurePosixPath(name)
    if p.is_absolute() or any(x in ("..", ".", "") for x in name.split("/")):
        raise KitError("Unsafe manifest path: " + name)
    return name

def no_symlinks(path: Path) -> None:
    p = Path(os.path.abspath(path.expanduser()))
    for node in [p, *p.parents]:
        if node.is_symlink():
            raise KitError("Refusing symlink path: " + str(node))

def verified_files(root: Path = ROOT) -> dict[str, bytes]:
    root = root.resolve()
    mf = root / "MANIFEST.json"
    no_symlinks(mf)
    try:
        doc = json.loads(mf.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise KitError("Missing or invalid MANIFEST.json") from exc
    if doc.get("schema") != 1 or not isinstance(doc.get("files"), dict):
        raise KitError("Unsupported manifest")
    output: dict[str, bytes] = {}
    for rel, expected in doc["files"].items():
        validate_rel(rel)
        p = root / rel
        no_symlinks(p)
        if not p.is_file():
            raise KitError("Missing file: " + rel)
        data = p.read_bytes()
        if digest(data) != expected:
            raise KitError("Modified file: " + rel + "; do not regenerate manifest blindly")
        output[rel] = data
    if SKILL_PREFIX + "SKILL.md" not in output:
        raise KitError("Required skill is missing")
    output["MANIFEST.json"] = mf.read_bytes()
    return output

def skill_payload(files: dict[str, bytes]) -> dict[str, bytes]:
    return {k[len(SKILL_PREFIX):]: v for k, v in files.items() if k.startswith(SKILL_PREFIX)}

def destination(scope: str, layout: str, project: str | None,
                home: Path | None = None, codex_home: str | None = None) -> Path:
    home = home or Path.home()
    if scope == "project":
        if layout != "modern" or not project:
            raise KitError("Project install requires --project and modern layout")
        p = Path(os.path.abspath(Path(project).expanduser()))
        no_symlinks(p)
        if not p.is_dir():
            raise KitError("Project directory must already exist")
        return p / ".agents" / "skills" / SKILL_NAME
    if scope != "user":
        raise KitError("Unknown scope")
    if project:
        raise KitError("--project is only for project scope")
    if layout == "modern":
        base = home / ".agents" / "skills"
    elif layout == "legacy":
        base = Path(codex_home or os.environ.get("CODEX_HOME") or str(home / ".codex")) / "skills"
    else:
        raise KitError("Unknown layout")
    return Path(os.path.abspath(base.expanduser())) / SKILL_NAME

def install_payload(payload: dict[str, bytes], dest: Path, apply: bool = False) -> str:
    """Install one self-contained directory atomically. Never overwrite."""
    no_symlinks(dest)
    for rel in payload:
        validate_rel(rel)
    if not payload or "SKILL.md" not in payload:
        raise KitError("Invalid skill payload")
    if dest.exists():
        if not dest.is_dir():
            raise KitError("Destination is not a directory")
        actual: dict[str, bytes] = {}
        for p in dest.rglob("*"):
            no_symlinks(p)
            if p.is_file():
                actual[p.relative_to(dest).as_posix()] = p.read_bytes()
        if actual == payload:
            return "already-identical"
        raise KitError("Existing skill differs; refusing to overwrite: " + str(dest))
    if not apply:
        return "would-install"
    dest.parent.mkdir(parents=True, exist_ok=True)
    no_symlinks(dest.parent)
    stage = Path(tempfile.mkdtemp(prefix=".product-sprint-stage-", dir=dest.parent))
    try:
        for rel, data in payload.items():
            p = stage / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        if dest.exists() or dest.is_symlink():
            raise KitError("Destination appeared during installation; retry after inspection")
        stage.rename(dest)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return "installed"
