"""Shared Jinja2 environment builder for codegen templates."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def make_env(templates_dir: Path, filters: dict) -> Environment:
    """Create a Jinja2 environment for a given templates directory."""
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters.update(filters)
    return env
