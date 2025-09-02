#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/jotaene/projects/automating-discobolo"
VENV_DIR="$PROJECT_DIR/venv"
LOG="$PROJECT_DIR/logs/run_birthdays.log"
LOCKFILE="/tmp/run_birthdays.lock"

# Ensure logs dir
mkdir -p "$PROJECT_DIR/logs"

# Serialize runs (avoid overlap)
exec 9>"$LOCKFILE"
flock -n 9 || { echo "[$(date)] Another run is in progress; exiting." >> "$LOG"; exit 0; }

# Minimal, deterministic env for cron
export TZ="America/Argentina/Buenos_Aires"
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export PYTHONPATH="$PROJECT_DIR"
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

cd "$PROJECT_DIR"

# If cron inherited a stale venv, drop it
unset VIRTUAL_ENV || true

{
  echo "============================================================"
  echo "[$(date)] Script started"

  echo "Env snapshot (trimmed for cron):"
  printf "HOME=%s\nLANG=%s\nTZ=%s\nPATH=%s\n" "$HOME" "$LANG" "$TZ" "$PATH"

  # Activate the correct venv
  if [[ -f "$VENV_DIR/bin/activate" ]]; then
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
  else
    echo "ERROR: venv not found at $VENV_DIR" ; exit 1
  fi

  echo "VIRTUAL_ENV: ${VIRTUAL_ENV:-<none>}"
  echo "Python being used:"
  command -v python3 || echo "python3 not found in PATH"
  python3 -V || true

  echo "Reached discobolo birthdays execution point"

  # Run your CLI if it’s installed in the venv
  echo "[discobolo] birthdays subcommand…"
  if command -v discobolo >/dev/null 2>&1; then
    discobolo birthdays
  else
    echo "WARN: 'discobolo' CLI not found on PATH; skipping this step."
  fi

  # Run the Python script with absolute path via the venv's python
  echo "[python] birthday_google.py…"
  "$VIRTUAL_ENV/bin/python" "$PROJECT_DIR/discobolo/scripts/birthdays/birthday_google.py"

  echo "[$(date)] Script finished"
} >> "$LOG" 2>&1
