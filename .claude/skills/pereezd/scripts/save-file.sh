#!/usr/bin/env bash
# Сохраняет файл из чата и пишет строку в реестр sessions/files/INDEX.md, чтобы следующая
# сессия взяла его отсюда, а не просила прислать снова.
#
#   save-file.sh [--no-pii] <файл> "<что важного одной строкой>" [откуда]
#       копия в sessions/files/<дата>-<имя> + строка в реестре + git add
#   save-file.sh --link <ссылка> <файл> "<что важного>" [откуда]
#       приватное или больше 50 МБ: копии нет, в реестре ссылка и sha256 оригинала
#
# PEREEZD_PUBLIC_REPO=1 (публичный репозиторий): копия только с --no-pii, то есть после
# проверки, что в файле нет персональных данных, цен, договоров и токенов.
# Дубли по sha256 пропускаются. Корень: $CLAUDE_PROJECT_DIR, иначе git, иначе текущая папка.
set -euo pipefail
link=""; nopii=0
while [ $# -gt 0 ]; do
  case "$1" in
    --link) link="${2:?ссылка после --link}"; shift 2 ;;
    --no-pii) nopii=1; shift ;;
    *) break ;;
  esac
done
src="${1:?путь к файлу}"; note="${2:?что в файле одной строкой}"; from="${3:-чат}"
clean() { printf '%s' "$1" | tr '\n\r|' '  /'; }
note="$(clean "$note")"; from="$(clean "$from")"
[ -f "$src" ] || { echo "нет файла: $src" >&2; exit 1; }
root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
dir="$root/sessions/files"; idx="$dir/INDEX.md"
if command -v sha256sum >/dev/null; then sum="$(sha256sum "$src" | cut -c1-12)"
else sum="$(shasum -a 256 "$src" | cut -c1-12)"; fi
bytes="$(wc -c < "$src" | tr -d ' ')"
size="$(awk -v b="$bytes" 'BEGIN{split("B K M G",u);i=1;while(b>=1024&&i<4){b/=1024;i++};printf "%.1f%s",b,u[i]}')"
if [ -z "$link" ]; then
  if [ "$bytes" -gt $((50*1024*1024)) ]; then
    echo "больше 50 МБ: в git не кладу. Загрузи в хранилище и повтори с --link <ссылка>" >&2; exit 2
  fi
  if [ "${PEREEZD_PUBLIC_REPO:-0}" = 1 ] && [ "$nopii" != 1 ]; then
    echo "репозиторий публичный: проверь файл на ПДн, цены, договоры, токены." >&2
    echo "чисто - повтори с --no-pii; приватное - --link <ссылка на приватное хранилище>" >&2; exit 3
  fi
fi
mkdir -p "$dir"
[ -f "$idx" ] || printf '%s\n\n%s\n%s\n' \
  '# Реестр файлов из чатов. Новая сессия берёт файлы отсюда и не просит их повторно.' \
  '| Файл | Откуда | Размер | sha256 (12) | Дата | Что важного |' \
  '|---|---|---|---|---|---|' > "$idx"
if grep -q "| $sum |" "$idx"; then
  echo "уже в реестре: $(grep "| $sum |" "$idx" | head -1 | cut -d'|' -f2 | xargs)"; exit 0
fi
base="$(basename "$src" | tr ' |' '__')"
if [ -n "$link" ]; then
  where="$(clean "$link") (оригинал: $base)"
else
  name="$(date +%F)-$base"
  [ -e "$dir/$name" ] && name="$(date +%F)-$sum-$base"
  cp -p "$src" "$dir/$name"
  where="\`sessions/files/$name\`"
fi
printf '| %s | %s | %s | %s | %s | %s |\n' "$where" "$from" "$size" "$sum" "$(date +%F)" "$note" >> "$idx"
git -C "$root" add sessions/files 2>/dev/null || true
echo "в реестре: $where. Закоммить и запушь в этом же ходе."
