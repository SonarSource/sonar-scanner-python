from __future__ import annotations

"""Utility helpers for tests that need an isolated real file-system sandbox.

TempFS provides a very small subset of the pyfakefs `fs` API that existing
unit-tests relied on (`create_file`, `create_dir`, `exists`, `chmod`).

Each TempFS instance is bound to a real temporary directory supplied by the
caller.  All paths passed to its methods are interpreted as *relative* to that
base directory; a leading slash ("/") is tolerated and stripped to simplify
migration (so that test code can stay almost identical).

Example
-------

    >>> tmp = tempfile.TemporaryDirectory()
    >>> fs = TempFS(Path(tmp.name))
    >>> fs.create_file("/hello.txt", contents="hi")
    >>> assert fs.exists("hello.txt")

The helper never cleans up the underlying directory; the caller (typically a
`tempfile.TemporaryDirectory`) owns the lifecycle.
"""

from pathlib import Path
from typing import Union

__all__ = ["TempFS"]


class TempFS:
    """Very thin wrapper around an actual directory on disk."""

    def __init__(self, base_dir: Path):
        if not base_dir.is_absolute():
            raise ValueError("base_dir must be an absolute Path")
        self.base_dir = base_dir
        # Ensure the directory exists; `TemporaryDirectory` already does, but be safe.
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------------
    # Public helper methods (mirrors of pyfakefs' minimal surface we need)
    # ---------------------------------------------------------------------
    def create_file(
        self, rel_path: Union[str, Path], *, contents: Union[str, bytes] | None = None
    ) -> Path:
        """Create a file inside the sandbox and write optional *contents*."""
        file_path = self._resolve(rel_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Choose binary/text mode automatically
        if contents is None:
            file_path.touch()
        else:
            if isinstance(contents, (bytes, bytearray)):
                mode = "wb"
            else:
                mode = "w"
            with open(file_path, mode) as fp:  # noqa: PTH123
                fp.write(contents)  # type: ignore[arg-type]
        return file_path

    def create_dir(self, rel_path: Union[str, Path]) -> Path:
        dir_path = self._resolve(rel_path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    def exists(self, rel_path: Union[str, Path]) -> bool:
        return self._resolve(rel_path).exists()

    def chmod(
        self,
        rel_path: Union[str, Path],
        mode: int,
        *,
        force_unix_mode: bool | None = None,
    ) -> None:  # noqa: D401,E501
        """Change permissions of a file/dir inside the sandbox.

        The *force_unix_mode* argument is ignored; it's only present so that
        existing calls that passed it (from pyfakefs) keep working.
        """
        self._resolve(rel_path).chmod(mode)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve(self, rel_path: Union[str, Path]) -> Path:
        if isinstance(rel_path, Path):
            rel_str = str(rel_path)
        else:
            rel_str = rel_path
        # Strip a possible leading slash so tests can keep absolute-looking paths
        rel_str = rel_str.lstrip("/")
        return self.base_dir / rel_str
