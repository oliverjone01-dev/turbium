#!/usr/bin/env bash
# Собирает архивы для раздачи:
#   dist/pereezd-skill.zip           - только скилл (claude.ai: Настройки -> Навыки)
#   dist/pereezd-plugin.zip          - плагин целиком (скилл + /pereezd + датчик-хук)
#   dist/pereezd-plugin-portable.zip - то же для другой учётки: без привязок к TURBIUM
set -euo pipefail
cd "$(dirname "$0")"
rm -rf dist && mkdir -p dist
(cd skills && zip -qrX ../dist/pereezd-skill.zip pereezd)
zip -qrX dist/pereezd-plugin.zip .claude-plugin skills commands hooks README.md
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
cp -r .claude-plugin skills commands hooks README.md "$tmp/"
sed -i '/<!-- own -->/,/<!-- \/own -->/d' "$tmp/README.md"
sed -i 's/"name": "TURBIUM"/"name": "pereezd"/' "$tmp/.claude-plugin/plugin.json"
sed -i "s/Вариант 3/Вариант 2/" "$tmp/README.md"
if grep -rqiE 'turbium|feniks|МЕА|ОЗОН|oliverjone' "$tmp"; then echo "в portable остались привязки:" >&2; grep -rniE 'turbium|feniks|МЕА|ОЗОН|oliverjone' "$tmp" >&2; exit 1; fi
(cd "$tmp" && zip -qrX "$OLDPWD/dist/pereezd-plugin-portable.zip" .claude-plugin skills commands hooks README.md)
for z in dist/*.zip; do echo "$z: $(unzip -l "$z" | tail -1 | awk '{print $2}') файлов"; done
