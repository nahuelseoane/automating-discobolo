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
def transfers(download: bool = typer.Option(False), update: bool = typer.Option(False)):
    """Download and/or update Bank Movements"""

    if download:
        typer.echo("📥 Downloading bank movements")
        subprocess.run(
            ["./venv/bin/python", "scripts/bank_movements_download.py"])

    if update:
        typer.echo("📝 Updating transfer file.")
        subprocess.run(
            ["./venv/bin/python", "scripts/transfer_file_update.py"])


@app.command()
def jefe_de_grupo():
    """Update column 'Jefe de Grupo' in transfers file."""
    typer.echo("📝 Updating 'Jefe de Grupo' in transfer file...")
    subprocess.run(["./venv/bin/python", "scripts/jefe_de_grupo_update.py"])


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


if __name__ == '__main__':
    app()
