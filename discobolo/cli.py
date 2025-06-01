# discobolo/cli.py
import typer
import subprocess

app = typer.Typer()


@app.command()
def run():
    """Run full automation pipeline"""
    typer.echo("▶ Running full automation pipeline")
    subprocess.run(["bash", "bin/automation_pipeline.sh"])


@app.command()
def transfers(download1: bool = typer.Option(False), download2: bool = typer.Option(False), update1: bool = typer.Option(False), update2: bool = typer.Option(False)):
    """Download and/or update Bank Movements"""

    if download1:
        typer.echo("📥 Downloading bank movements")
        subprocess.run(
            ["./venv/bin/python", "scripts/transfers_download.py"])

    if download2:
        typer.echo("📥 Bank file renaming complete.")
        subprocess.run(
            ["./venv/bin/python", "scripts/transfers_download_renaming.py"])

    if update1:
        typer.echo("📝 Updating transfer file with data.")
        subprocess.run(
            ["./venv/bin/python", "scripts/transfers_update.py"])

    if update2:
        typer.echo("📝 Updating transfer file with 'Jefe de Grupo'.")
        subprocess.run(
            ["./venv/bin/python", "scripts/transfers_update_2.py"])


@app.command()
def emails():
    """Send payment emails only"""
    typer.echo("✉️ Sending emails...")
    subprocess.run(["./venv/bin/python", "scripts/email_sending_automate.py"])


@app.command()
def sytech():
    """Uploading user's payments into Sytech system."""
    typer.echo("💳 Uploading payments...")
    subprocess.run(["./venv/bin/python", "scripts/sytech_automate.py"])


@app.command()
def morosos(download: bool = typer.Option(False), update: bool = typer.Option(False)):
    """Download and/or update Morosos file"""
    if download:
        typer.echo("📥 Downloading morosos file...")
        subprocess.run(["./venv/bin/python", "scripts/morosos_download.py"])

    if update:
        typer.echo("📝 Updating morosos file...")
        subprocess.run(["./venv/bin/python", "scripts/morosos_update.py"])


@app.command()
def recurrentes(download: bool = typer.Option(False), update: bool = typer.Option(False)):
    """Download and/or update Recurrentes file"""
    if download:
        typer.echo("📥 Downloading 'Recurrentes' report...")
        subprocess.run(
            ["./venv/bin/python", "scripts/recurrentes_download.py"])

    if update:
        typer.echo("📝 Updating 'Recurrentes' file...")
        subprocess.run(["./venv/bin/python", "scripts/recurrentes_update.py"])


if __name__ == '__main__':
    app()
