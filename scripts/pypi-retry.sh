#!/usr/bin/env bash
# ============================================================================
# PyPI Auto-Retry Script
# Keeps trying to upload to PyPI until the rate limit clears
# ============================================================================

set -euo pipefail

cd /Users/nicholas/clawd/meok-sdk-python

echo "=== PyPI Auto-Retry for meok-sdk ==="
echo "Package: meok-sdk-3.1.0"
echo ""

ATTEMPT=1
MAX_ATTEMPTS=50
SLEEP_SECONDS=300  # 5 minutes between attempts

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "Attempt $ATTEMPT/$MAX_ATTEMPTS..."
    
    if python3 -m twine upload dist/* 2>&1 | grep -q "Uploading"; then
        echo ""
        echo "🎉 SUCCESS! Package uploaded to PyPI"
        echo "Install with: pip install meok-sdk==3.1.0"
        exit 0
    fi
    
    echo "❌ Rate limit still active. Waiting ${SLEEP_SECONDS}s..."
    sleep $SLEEP_SECONDS
    ATTEMPT=$((ATTEMPT + 1))
done

echo ""
echo "⚠️  Max attempts reached. PyPI rate limit still active."
echo "Try again later with: cd /Users/nicholas/clawd/meok-sdk-python && python3 -m twine upload dist/*"
exit 1
