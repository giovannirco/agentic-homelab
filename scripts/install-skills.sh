#!/usr/bin/env bash
# Install agentic-homelab skills into Grok, Hermes and/or Claude Code skill dirs.
#
# Usage:
#   bash scripts/install-skills.sh
#   bash scripts/install-skills.sh --hermes
#   bash scripts/install-skills.sh --grok
#   bash scripts/install-skills.sh --claude   # ~/.claude/skills (restart the CLI afterwards)
#   bash scripts/install-skills.sh --both     # Grok + Hermes
#   bash scripts/install-skills.sh --all      # Grok + Hermes + Claude Code
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
    --claude) MODE="claude" ;;
    --both)   MODE="both" ;;
    --all)    MODE="all" ;;
    -h|--help)
      sed -n '2,11p' "$0"
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
  claude) install_to "${HOME}/.claude/skills" ;;
  all)
    install_to "${HOME}/.grok/skills"
    install_to "${HOME}/.hermes/skills"
    install_to "${HOME}/.claude/skills"
    ;;
  both)
    install_to "${HOME}/.grok/skills"
    install_to "${HOME}/.hermes/skills"
    ;;
  grok|*) install_to "${HOME}/.grok/skills" ;;
esac
