"""Download and cache OpenRCT2 source for a given version tag."""

from pathlib import Path

REPO_URL = "https://github.com/OpenRCT2/OpenRCT2.git"
CACHE_DIR = Path.home() / ".cache" / "openrct2-actiongen"

# Minimum expected files — sanity check after download
MIN_ACTION_FILES = 50


def get_cache_path(version: str) -> Path:
    """Return the cache directory for a given version tag."""
    return CACHE_DIR / version


def get_source(version: str | None = None, local_path: Path | None = None) -> Path:
    """Get path to OpenRCT2 source root.

    Either downloads the source for a version tag (sparse clone),
    or validates and returns a local path.
    """
    if local_path and version:
        raise ValueError("Provide either --openrct2-version or --openrct2-source, not both.")

    if local_path:
        return _use_local(local_path)

    if version:
        return _download(version)

    raise ValueError("Provide either --openrct2-version or --openrct2-source.")


def _use_local(path: Path) -> Path:
    """Validate and return a local source path."""
    if not path.is_dir():
        raise FileNotFoundError(f"Source path does not exist: {path}")
    _validate_source(path)
    return path


def _download(version: str) -> Path:
    """Download source via sparse clone, or return cached path."""
    cache_path = get_cache_path(version)
    if cache_path.exists():
        _validate_source(cache_path)
        return cache_path
    raise NotImplementedError("Sparse clone not yet implemented")


def _validate_source(source_root: Path) -> None:
    """Sanity-check that the source has the files we need."""
    script_engine = source_root / "src" / "openrct2" / "scripting" / "ScriptEngine.cpp"
    if not script_engine.exists():
        raise FileNotFoundError(f"ScriptEngine.cpp not found at {script_engine}")

    action_files = list(source_root.glob("src/openrct2/actions/**/*Action.cpp"))
    if len(action_files) < MIN_ACTION_FILES:
        raise FileNotFoundError(
            f"Expected at least {MIN_ACTION_FILES} action files, found {len(action_files)}"
        )
