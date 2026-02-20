#!/bin/bash
# Daily analytics workflow: fetch data, generate report, send to Telegram

set -e

ANALYTICS_DIR="/home/delmar/.openclaw/workspace/projects/altclaw/analytics"
cd "$ANALYTICS_DIR"

echo "📊 Running daily analytics workflow..."

# 1. Fetch analytics from GA4
echo "1/3 Fetching analytics from GA4..."
./fetch_analytics.py

# 2. Generate report
echo "2/3 Generating report..."
REPORT=$(./generate_report.py)

# 3. Send to Telegram using OpenClaw message tool
echo "3/3 Sending to Telegram..."
echo "$REPORT"

# Return report for OpenClaw to capture
exit 0
