#!/usr/bin/env bash
# Сохраняет файл из чата в проект и пишет строку в реестр sessions/files/INDEX.md,
# чтобы следующая сессия взяла его отсюда, а не просила прислать снова.
# Использование: save-file.sh <путь-к-файлу> "<что важного одной строкой>" [откуда]
# Повторный вызов с тем же содержимым ничего не дублирует (сверка по sha256).
set -euo pipefail
src="${1:?путь к файлу}"; note="${2:?что в файле одной строкой}"; note="${note//|//}"; from="${3:-чат}"
[ -f "$src" ] || { echo "нет файла: $src" >&2; exit 1; }
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
dir="$root/sessions/files"; idx="$dir/INDEX.md"
mkdir -p "$dir"
[ -f "$idx" ] || printf '%s\n\n%s\n%s\n' \
  '# Реестр файлов из чатов. Новая сессия берёт файлы отсюда и не просит их повторно.' \
  '| Файл | Откуда | Размер | sha256 (12) | Дата | Что важного |' \
  '|---|---|---|---|---|---|' > "$idx"
sum="$(sha256sum "$src" | cut -c1-12)"
if grep -q "| $sum |" "$idx"; then
  echo "уже в реестре: $(grep "| $sum |" "$idx" | cut -d'|' -f2 | xargs)"; exit 0
fi
name="$(date +%F)-$(basename "$src" | tr ' ' '_')"
cp -p "$src" "$dir/$name"
size="$(du -h "$dir/$name" | cut -f1)"
printf '| `sessions/files/%s` | %s | %s | %s | %s | %s |\n' \
  "$name" "$from" "$size" "$sum" "$(date +%F)" "$note" >> "$idx"
echo "сохранён: sessions/files/$name"
