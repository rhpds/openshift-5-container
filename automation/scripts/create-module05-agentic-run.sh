#!/usr/bin/env bash
# Instructor compatibility wrapper. Only creates analysis, no execution.
set -euo pipefail
[[ "$#" -eq 1 ]] || { echo "Usage: bash create-module05-agentic-run.sh user-<guid>" >&2; exit 2; }
bash "$(dirname "$0")/create-weather-agentic-run.sh" 5 "$1"
