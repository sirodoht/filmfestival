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

echo "=== Installing Caddy ==="
ssh "$REMOTE_HOST" 'apt-get update && apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl'
ssh "$REMOTE_HOST" "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg"
ssh "$REMOTE_HOST" "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list"
ssh "$REMOTE_HOST" 'chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg /etc/apt/sources.list.d/caddy-stable.list'
ssh "$REMOTE_HOST" 'apt-get update && apt-get install -y caddy'

echo "=== Creating www directory ==="
ssh "$REMOTE_HOST" 'mkdir -p /var/www/filmfestival && chmod 0755 /var/www /var/www/filmfestival'

echo "=== Creating deploy user ==="
ssh "$REMOTE_HOST" 'id deploy >/dev/null 2>&1 || useradd -m -s /bin/bash -N -G www-data deploy; usermod -a -G www-data deploy; usermod -L deploy'

echo "=== Generating SSH key for deploy user ==="
ssh "$REMOTE_HOST" 'install -d -m 0700 -o deploy -g deploy /home/deploy/.ssh && test -f /home/deploy/.ssh/id_ed25519 || su - deploy -c "ssh-keygen -t ed25519 -f /home/deploy/.ssh/id_ed25519 -N \"\""'

echo "=== Setting www ownership ==="
ssh "$REMOTE_HOST" 'chown -R deploy:www-data /var/www/filmfestival'

echo "=== Installing Caddy configuration ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_CADDYFILE="$(mktemp)"
trap 'rm -f "$TEMP_CADDYFILE"' EXIT
sed "s/yourdomain\.com/$SITE_DOMAIN/" "$SCRIPT_DIR/Caddyfile" > "$TEMP_CADDYFILE"
scp "$TEMP_CADDYFILE" "$REMOTE_HOST:/etc/caddy/Caddyfile"
ssh "$REMOTE_HOST" 'caddy fmt --overwrite /etc/caddy/Caddyfile && caddy validate --config /etc/caddy/Caddyfile'
ssh "$REMOTE_HOST" 'systemctl enable --now caddy && systemctl reload caddy'

echo "=== Removing obsolete application service ==="
ssh "$REMOTE_HOST" 'systemctl disable --now filmfestival.service >/dev/null 2>&1 || true; rm -f /etc/systemd/system/filmfestival.service; systemctl daemon-reload'

echo "=== Provisioning complete! ==="
echo "Add this deploy key to the GitHub repository, then clone it into /var/www/filmfestival:"
ssh "$REMOTE_HOST" 'cat /home/deploy/.ssh/id_ed25519.pub'
