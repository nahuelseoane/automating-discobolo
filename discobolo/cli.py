# discobolo/cli.py
import subprocess
from pathlib import Path

import typer

from discobolo.scripts.email_sending_automate import send_emails
from discobolo.scripts.morosos_download import run_morosos_download
from discobolo.scripts.morosos_update import run_morosos_update
from discobolo.scripts.recurrentes_download import run_recurrentes_download
from discobolo.scripts.recurrentes_update import run_recurrentes_update
from discobolo.scripts.sytech_automate import run_sytech_automation
from discobolo.scripts.transfers_download import run_transfers_download
from discobolo.scripts.transfers_renaming import (
    run_transfers_renaming,
)
from discobolo.scripts.transfers_update import run_transfers_update
from discobolo.scripts.transfers_update_2 import run_transfers_update_2

app = typer.Typer()


@app.command()
def run():
    """Run full automation pipeline"""
    typer.echo("▶ Running full automation pipeline")

    project_root = Path(__file__).resolve().parent.parent
    script_path = project_root / "bin" / "automation_pipeline.sh"

    subprocess.run(["bash", str(script_path)])


@app.command()
def transfers(
    download: bool = typer.Option(False),
    renaming: bool = typer.Option(False),
    update1: bool = typer.Option(False),
    update2: bool = typer.Option(False),
):
    """Download and/or update Bank Movements"""

    if download:
        typer.echo("📥 Downloading bank movements")
        run_transfers_download()

    if renaming:
        typer.echo("📥 Bank file renaming complete.")
        run_transfers_renaming()

    if update1:
        typer.echo("📝 Updating transfer file with data.")
        run_transfers_update()

    if update2:
        typer.echo("📝 Updating transfer file with 'Jefe de Grupo'.")
        run_transfers_update_2()


@app.command()
def emails():
    """Send payment emails only"""
    typer.echo("✉️ Sending emails...")
    send_emails()


@app.command()
def sytech():
    """Uploading users's payments into Sytech system."""
    typer.echo("💳 Uploading payments...")
    run_sytech_automation()


@app.command()
def morosos(download: bool = typer.Option(False), update: bool = typer.Option(False)):
    """Download and/or update Morosos file"""
    if download:
        typer.echo("📥 Downloading morosos file...")
        run_morosos_download()

    if update:
        typer.echo("📝 Updating morosos file...")
        run_morosos_update()


@app.command()
def recurrentes(
    download: bool = typer.Option(False), update: bool = typer.Option(False)
):
    """Download and/or update Recurrentes file"""
    if download:
        typer.echo("📥 Downloading 'Recurrentes' report...")
        run_recurrentes_download()

    if update:
        typer.echo("📝 Updating 'Recurrentes' file...")
        run_recurrentes_update()


@app.command()
def check():
    """Check if drive folder is accessible"""
    typer.echo("👌 Checking if driver folder is accessible.")
    subprocess.run(["bash", "discobolo/scripts/check_and_remount.sh"], check=True)


if __name__ == "__main__":
    app()
