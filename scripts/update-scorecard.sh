#!/usr/bin/env bash
# scripts/update-scorecard.sh
# Regenerates src/_data/securityclaw_scorecard.json from SecurityClaw campaigns.db
#
# Run before building/deploying to ensure scorecard data is current:
#   ./scripts/update-scorecard.sh && ./deploy-to-s3.sh
#
# Requires: python3, SecurityClaw campaigns.db accessible at the default path.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_DIR="$(dirname "$SCRIPT_DIR")"

DB_PATH="/home/delmar/.openclaw/agents/peng/workspace/projects/security/campaign-manager/campaigns.db"
OUT_PATH="$SITE_DIR/src/_data/securityclaw_scorecard.json"

echo "🔄 Regenerating SecurityClaw scorecard..."
python3 "$SCRIPT_DIR/generate_scorecard.py" --db "$DB_PATH" --out "$OUT_PATH"
echo "✅ Scorecard updated: $OUT_PATH"
