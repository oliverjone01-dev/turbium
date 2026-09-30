#!/usr/bin/env python3
"""Датчик контекста для скилла pereezd (хук UserPromptSubmit).

Перед каждым сообщением пользователя смотрит в транскрипт сессии, берёт размер
контекста из usage последнего ответа модели и, если сессия упёрлась в предел,
подмешивает в контекст указание выполнить переезд в новую сессию.

Пороги (токены контекста), переопределяются переменными окружения:
  PEREEZD_SOFT  - 150000: предложить переезд на ближайшей точке сохранения
  PEREEZD_HARD  - 200000: переезд обязателен до начала работы над запросом
  PEREEZD_IDLE_MIN - 60: пауза в минутах, после которой кэш уже остыл
  PEREEZD_IDLE_CTX - 100000: при остывшем кэше и таком контексте переезд почти бесплатен

Файлы из чата: если в папках загрузок лежат файлы, которых нет в реестре
sessions/files/INDEX.md, напоминает сохранить их (скрипт save-file.sh скилла) до работы.
В новой сессии с реестром напоминает, что файлы брать оттуда, а не просить снова.
  PEREEZD_UPLOAD_DIRS - папки загрузок через «:» (по умолчанию /mnt/user-data/uploads:/mnt/attach)

Отключить разово: в сообщении написать «без переезда».
Хук никогда не блокирует сообщение: при любой ошибке молча выходит с кодом 0.
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

SOFT = int(os.environ.get("PEREEZD_SOFT", 150_000))
HARD = int(os.environ.get("PEREEZD_HARD", 200_000))
IDLE_MIN = int(os.environ.get("PEREEZD_IDLE_MIN", 60))
IDLE_CTX = int(os.environ.get("PEREEZD_IDLE_CTX", 100_000))
UPLOAD_DIRS = os.environ.get("PEREEZD_UPLOAD_DIRS", "/mnt/user-data/uploads:/mnt/attach")
HASH_LIMIT = 50 * 1024 * 1024


def last_main_usage(path):
    """Возвращает (контекст в токенах, время ответа) последнего ответа основной ветки."""
    last = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            if '"assistant"' not in line or '"usage"' not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("type") != "assistant" or row.get("isSidechain"):
                continue
            usage = (row.get("message") or {}).get("usage") or {}
            ctx = (
                usage.get("input_tokens", 0)
                + usage.get("cache_read_input_tokens", 0)
                + usage.get("cache_creation_input_tokens", 0)
            )
            if ctx:
                last = (ctx, row.get("timestamp"))
    return last


def minutes_since(ts):
    if not ts:
        return 0
    then = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - then).total_seconds() / 60


def sha12(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def unsaved_uploads(registry):
    """Файлы из папок загрузок, которых нет в реестре (по sha256 или имени)."""
    out = []
    for d in UPLOAD_DIRS.split(":"):
        if not d or not os.path.isdir(d):
            continue
        for base, _, names in os.walk(d):
            for n in names:
                fp = os.path.join(base, n)
                try:
                    if os.path.getsize(fp) <= HASH_LIMIT:
                        known = f"| {sha12(fp)} |" in registry
                    else:
                        known = n.replace(" ", "_") in registry
                except OSError:
                    continue
                if not known:
                    out.append(fp)
                if len(out) >= 20:
                    return out
    return out


def files_note(root, new_session):
    idx = os.path.join(root, "sessions", "files", "INDEX.md")
    registry = ""
    if os.path.exists(idx):
        with open(idx, encoding="utf-8", errors="ignore") as f:
            registry = f.read()
    notes = []
    fresh = unsaved_uploads(registry)
    if fresh:
        notes.append(
            "[pereezd] В чате файлы, которых нет в реестре sessions/files/INDEX.md: "
            + ", ".join(fresh)
            + ". Сохрани их скриптом scripts/save-file.sh скилла pereezd в этом же ходе, "
            "чтобы следующая сессия не просила их повторно."
        )
    if new_session and registry:
        count = sum(1 for line in registry.splitlines() if line.startswith("| `"))
        notes.append(
            f"[pereezd] Реестр файлов из прошлых чатов: sessions/files/INDEX.md ({count} шт.). "
            "Нужный файл бери оттуда, пользователя повторно не проси."
        )
    return notes


def main():
    data = json.load(sys.stdin)
    if "без переезда" in (data.get("prompt") or "").lower():
        return
    path = data.get("transcript_path")
    if not path or not os.path.exists(path):
        return
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    found = last_main_usage(path)
    notes = files_note(root, new_session=not found)
    if not found:
        emit(notes)
        return
    ctx, ts = found
    idle = minutes_since(ts)
    k = f"{ctx // 1000}K"

    if ctx >= HARD:
        msg = (
            f"[pereezd] Контекст сессии {k} токенов, это выше жёсткого порога {HARD // 1000}K. "
            "ПЕРЕЕЗД ОБЯЗАТЕЛЕН: сначала выполни скилл pereezd (сохранить, передать, открыть "
            "новую сессию), а запрос пользователя передай в новую сессию дословно как первую "
            "задачу. Если сейчас идёт незавершённая правка - сначала доведи её до коммита. "
            "Файлы, присланные в этом сообщении, сначала сохрани в реестр, потом переезжай."
        )
    elif idle >= IDLE_MIN and ctx >= IDLE_CTX:
        msg = (
            f"[pereezd] Контекст {k}, пауза {int(idle)} мин: кэш остыл, следующий ход перечитает "
            "весь контекст по полной цене. Сейчас самый дешёвый момент для переезда. Если запрос "
            "начинает новую задачу или не требует памяти этой сессии - выполни скилл pereezd."
        )
    elif ctx >= SOFT:
        msg = (
            f"[pereezd] Контекст {k} из порога {HARD // 1000}K. Закончи текущий шаг и на ближайшей "
            "точке сохранения (коммит, закрытая подзадача, смена темы) выполни скилл pereezd, "
            "не дожидаясь жёсткого порога."
        )
    else:
        msg = None

    emit(notes + ([msg] if msg else []))


def emit(parts):
    if not parts:
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "\n".join(parts),
        }
    }, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
