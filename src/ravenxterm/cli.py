"""Command-line interface for RavenXTerm."""

import click

from . import __version__


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """RavenXTerm - A Local-First AI Terminal Extension."""


@cli.command()
def shell() -> None:
    """Start an interactive RavenXTerm shell."""
    click.echo("Starting RavenXTerm shell...")
    # TODO: Implement interactive shell


@cli.command()
@click.argument('command', required=False)
def explain(command: str | None) -> None:
    """Explain a shell command or concept."""
    if command:
        click.echo(f"Explaining command: {command}")
        # TODO: Implement command explanation
    else:
        click.echo("Please provide a command to explain")


@cli.command()
@click.argument('query')
def generate(query: str) -> None:
    """Generate a shell command from natural language."""
    click.echo(f"Generating command for: {query}")
    # TODO: Implement command generation


def main() -> None:
    """Main entry point for the CLI."""
    cli()
