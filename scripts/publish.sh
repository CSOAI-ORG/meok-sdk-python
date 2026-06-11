#!/usr/bin/env bash
# MEOK SDK Python — PyPI Publish Script
# Usage: ./scripts/publish.sh [patch|minor|major]
# Default bump level: patch

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUMP="${1:-patch}"

cd "${ROOT_DIR}"

echo "🔍 Current version: $(grep -E '^version' pyproject.toml | head -1)"

# ── 1. Bump version in pyproject.toml ───────────────────────────────
echo "📦 Bumping ${BUMP} version..."
python3 -c "
import re, sys
with open('pyproject.toml') as f:
    text = f.read()

m = re.search(r'^version\s*=\s*\"(\d+)\.(\d+)\.(\d+)\"', text, re.M)
if not m:
    sys.exit('Could not parse version')

major, minor, patch = map(int, m.groups())
if '${BUMP}' == 'major':
    major += 1; minor = 0; patch = 0
elif '${BUMP}' == 'minor':
    minor += 1; patch = 0
else:
    patch += 1

new_ver = f'{major}.{minor}.{patch}'
text = re.sub(r'^version\s*=\s*\"[^\"]+\"', f'version = \"{new_ver}\"', text, count=1, flags=re.M)

with open('pyproject.toml', 'w') as f:
    f.write(text)

print(new_ver)
" > /tmp/new_version.txt

NEW_VERSION="$(cat /tmp/new_version.txt)"
echo "✅ New version: ${NEW_VERSION}"

# ── 2. Run tests ────────────────────────────────────────────────────
echo "🧪 Running tests..."
python3 -m pytest tests/ -q

# ── 3. Build wheel ────────────────────────────────────────────────────
echo "🔨 Building wheel..."
python3 -m build --wheel --sdist

# ── 4. Upload to PyPI ───────────────────────────────────────────────
echo "🚀 Uploading to PyPI..."
python3 -m twine upload dist/*"${NEW_VERSION}"*

# ── 5. Tag git release ──────────────────────────────────────────────
echo "🏷️  Tagging release v${NEW_VERSION}..."
git add pyproject.toml
git commit -m "release: v${NEW_VERSION}"
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"
git push origin main --tags

echo "🎉 meok-sdk-python v${NEW_VERSION} published successfully!"
