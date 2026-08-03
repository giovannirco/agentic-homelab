#!/usr/bin/env bash
# Install agentic-homelab skills into Grok and/or Hermes skill dirs.
#
# Usage:
#   bash scripts/install-skills.sh
#   bash scripts/install-skills.sh --hermes
#   bash scripts/install-skills.sh --grok
#   bash scripts/install-skills.sh --both
#   AGENTIC_HOMELAB_DEST=~/.custom/skills bash scripts/install-skills.sh
set -euo pipefail

MODE="grok"
if [[ -n "${AGENTIC_HOMELAB_DEST:-}" ]]; then
  MODE="custom"
fi
for arg in "$@"; do
  case "$arg" in
    --hermes) MODE="hermes" ;;
    --grok)   MODE="grok" ;;
    --both)   MODE="both" ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$ROOT/skills"

if [[ ! -d "$SRC" ]]; then
  echo "No skills/ at $SRC" >&2
  exit 1
fi

install_to() {
  local DEST="$1"
  mkdir -p "$DEST"
  for d in "$SRC"/*/; do
    [[ -d "$d" ]] || continue
    name="$(basename "$d")"
    echo "Installing skill: $name → $DEST/$name"
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --delete "$d" "$DEST/$name/"
    else
      rm -rf "$DEST/$name"
      mkdir -p "$DEST/$name"
      cp -R "$d"/* "$DEST/$name/"
    fi
  done
  echo "Done → $DEST"
  ls -1 "$DEST"
}

case "$MODE" in
  custom) install_to "${AGENTIC_HOMELAB_DEST}" ;;
  hermes) install_to "${HOME}/.hermes/skills" ;;
  both)
    install_to "${HOME}/.grok/skills"
    install_to "${HOME}/.hermes/skills"
    ;;
  grok|*) install_to "${HOME}/.grok/skills" ;;
esac
