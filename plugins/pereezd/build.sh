#!/usr/bin/env bash
# Собирает архивы для раздачи коллегам:
#   dist/pereezd-skill.zip  - только скилл (загрузка в claude.ai: Настройки -> Навыки)
#   dist/pereezd-plugin.zip - плагин целиком (скилл + /pereezd + датчик-хук)
set -euo pipefail
cd "$(dirname "$0")"
rm -rf dist && mkdir -p dist
(cd skills && zip -qrX ../dist/pereezd-skill.zip pereezd)
zip -qrX dist/pereezd-plugin.zip .claude-plugin skills commands hooks README.md
unzip -l dist/pereezd-skill.zip | tail -n +4 | head -n -2
echo "---"
unzip -l dist/pereezd-plugin.zip | tail -n +4 | head -n -2
