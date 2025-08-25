#!/usr/bin/env bash
set -euo pipefail
ts=$(date -u +"%Y%m%dT%H%M%SZ")
mkdir -p ledger/archive
mv ledger/events.jsonl "ledger/archive/events_$ts.jsonl" || true
