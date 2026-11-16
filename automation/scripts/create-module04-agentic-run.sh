#!/usr/bin/env bash
# Instructor compatibility wrapper for WeatherNow Module 4.
set -euo pipefail
[[ "$#" -eq 1 ]] || { echo "Usage: bash create-module04-agentic-run.sh user-<guid>" >&2; exit 2; }
bash "$(dirname "$0")/create-weather-agentic-run.sh" 4 "$1"
