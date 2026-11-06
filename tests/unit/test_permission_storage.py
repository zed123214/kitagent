from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from agent_runtime.core.permissions.storage import load_policy_file, save_policy_file


def test_policy_save_creates_parent_and_replaces_previous_rules(tmp_path: Path) -> None:
    path = tmp_path / "config" / "policy.toml"

    save_policy_file({"write_file": "deny", "bash": "allow"}, path)

    assert load_policy_file(path) == {"bash": "allow", "write_file": "deny"}
    assert path.read_text(encoding="utf-8").endswith('bash = "allow"\nwrite_file = "deny"\n')
    save_policy_file({}, path)
    assert load_policy_file(path) == {}
    assert list(path.parent.iterdir()) == [path]


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("failure", ["encoding", "fsync", "replace"])
def test_failed_policy_save_preserves_previous_file_and_removes_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, existing: bool, failure: str
) -> None:
    path = tmp_path / "policy.toml"
    previous = b'[always]\nbash = "deny"\n'
    if existing:
        path.write_bytes(previous)

    def fail_fsync(_fd: int) -> None:
        raise OSError("injected fsync failure")

    def fail_replace(_source: Path, _target: Path) -> None:
        raise OSError("injected replace failure")

    if failure == "fsync":
        monkeypatch.setattr(os, "fsync", fail_fsync)
    elif failure == "replace":
        monkeypatch.setattr(os, "replace", fail_replace)

    rules = {"bash": "\ud800" if failure == "encoding" else "allow"}
    error = UnicodeEncodeError if failure == "encoding" else OSError
    with pytest.raises(error):
        save_policy_file(rules, path)

    if existing:
        assert path.read_bytes() == previous
        assert load_policy_file(path) == {"bash": "deny"}
    else:
        assert not path.exists()
    assert list(tmp_path.iterdir()) == ([path] if existing else [])


@pytest.mark.skipif(os.name == "nt", reason="creating symlinks may require Windows privileges")
def test_policy_save_preserves_symlink_and_updates_its_target(tmp_path: Path) -> None:
    target = tmp_path / "stored.toml"
    target.write_text('[always]\nbash = "deny"\n', encoding="utf-8")
    link = tmp_path / "policy.toml"
    link.symlink_to(target.name)

    save_policy_file({"bash": "allow"}, link)

    assert link.is_symlink()
    assert load_policy_file(target) == {"bash": "allow"}
    assert sorted(tmp_path.iterdir()) == sorted([link, target])


@pytest.mark.skipif(os.name == "nt", reason="POSIX mode bits are not supported on Windows")
@pytest.mark.parametrize("mode", [0o600, 0o640])
def test_policy_replace_preserves_existing_mode(tmp_path: Path, mode: int) -> None:
    path = tmp_path / "policy.toml"
    path.write_text('[always]\nbash = "deny"\n', encoding="utf-8")
    path.chmod(mode)

    save_policy_file({"bash": "allow"}, path)

    assert stat.S_IMODE(path.stat().st_mode) == mode
    assert load_policy_file(path) == {"bash": "allow"}
