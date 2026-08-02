#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
    echo "Usage: $0 <ssh-host> [site-domain]"
    echo "Example: $0 root@203.0.113.10 festival.example.com"
    exit 1
fi

REMOTE_HOST="$1"
SITE_DOMAIN="${2:-${REMOTE_HOST##*@}}"

if [[ ! "$SITE_DOMAIN" =~ ^[A-Za-z0-9.-]+$ ]]; then
    echo "Invalid site domain: $SITE_DOMAIN"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_CADDYFILE="$(mktemp)"
trap 'rm -f "$TEMP_CADDYFILE"' EXIT
sed "s/yourdomain\.com/$SITE_DOMAIN/" "$SCRIPT_DIR/Caddyfile" > "$TEMP_CADDYFILE"

echo "=== Updating static site ==="
ssh "$REMOTE_HOST" 'su - deploy -c "git -C /var/www/filmfestival pull --ff-only origin main"'

echo "=== Updating Caddy configuration ==="
scp "$TEMP_CADDYFILE" "$REMOTE_HOST:/etc/caddy/Caddyfile.filmfestival"
ssh "$REMOTE_HOST" 'caddy fmt --overwrite /etc/caddy/Caddyfile.filmfestival && caddy validate --adapter caddyfile --config /etc/caddy/Caddyfile.filmfestival && install -m 0644 /etc/caddy/Caddyfile.filmfestival /etc/caddy/Caddyfile && systemctl reload caddy'

echo "=== Removing obsolete application service ==="
ssh "$REMOTE_HOST" 'systemctl disable --now filmfestival.service >/dev/null 2>&1 || true; rm -f /etc/systemd/system/filmfestival.service /etc/caddy/Caddyfile.filmfestival; systemctl daemon-reload'

echo "=== Deployment complete! ==="
