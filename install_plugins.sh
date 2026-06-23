#!/usr/bin/env bash
# install_plugins.sh — bootstrap opencode config: bun, cc-safety-net, caveman.
# context-mode auto-installs itself via opencode; not handled here.
#
# Run from the repo root after a fresh clone, before first opencode launch.
set -euo pipefail

CAVEMAN_REPO="https://github.com/JuliusBrussee/caveman"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "==> [1/3] bun"
if command -v bun >/dev/null 2>&1; then
  echo "bun present: $(bun --version)"
else
  curl -fsSL https://bun.sh/install | bash
  export BUN_INSTALL="$HOME/.bun"
  export PATH="$BUN_INSTALL/bin:$PATH"
  echo "bun installed: $(bun --version)"
fi

echo "==> [2/3] cc-safety-net"
command -v opencode >/dev/null 2>&1 || {
  echo "ERROR: opencode CLI not on PATH. Install opencode first." >&2
  exit 1
}
opencode plugin -g cc-safety-net

echo "==> [3/3] caveman"
git clone --depth 1 "$CAVEMAN_REPO" "$TMPDIR/caveman"
bun "$TMPDIR/caveman/bin/install.js" --only opencode

echo "==> done. context-mode installs itself automatically via opencode."
