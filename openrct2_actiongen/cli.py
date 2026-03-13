"""CLI entry point for openrct2-actiongen."""

import json
from pathlib import Path

import click

from openrct2_actiongen.parser import parse_actions
from openrct2_actiongen.source import get_source


@click.group()
def main() -> None:
    """Parse OpenRCT2 C++ source to generate action binding definitions."""


@main.command()
@click.option(
    "--openrct2-version",
    type=str,
    default=None,
    help="OpenRCT2 version tag to download (e.g. v0.4.32).",
)
@click.option(
    "--openrct2-source",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to local OpenRCT2 source checkout.",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=Path("actions.json"),
    help="Output path for actions.json.",
    show_default=True,
)
@click.option("--verbose", is_flag=True, help="Show detailed progress.")
def generate(
    openrct2_version: str | None,
    openrct2_source: Path | None,
    output: Path,
    verbose: bool,
) -> None:
    """Generate actions.json from OpenRCT2 source."""
    source_root = get_source(version=openrct2_version, local_path=openrct2_source)
    version = openrct2_version or source_root.name

    click.echo(f"Parsing {version} source at {source_root}")
    ir = parse_actions(source_root, version=version)
    click.echo(f"Parsed {len(ir.actions)} actions")

    output.write_text(json.dumps(ir.model_dump(), indent=2) + "\n")
    click.echo(f"Written to {output}")
