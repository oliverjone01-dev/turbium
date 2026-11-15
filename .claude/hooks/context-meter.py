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
import re
import subprocess
import sys
from datetime import datetime, timezone

SOFT = int(os.environ.get("PEREEZD_SOFT", 150_000))
HARD = int(os.environ.get("PEREEZD_HARD", 200_000))
IDLE_MIN = int(os.environ.get("PEREEZD_IDLE_MIN", 60))
IDLE_CTX = int(os.environ.get("PEREEZD_IDLE_CTX", 100_000))
UPLOAD_DIRS = os.environ.get("PEREEZD_UPLOAD_DIRS", "/mnt/user-data/uploads:/mnt/attach")
HASH_LIMIT = 50 * 1024 * 1024
HASH_BUDGET = 200 * 1024 * 1024  # сколько байт новых файлов хэшировать за один запуск
CACHE = os.path.join(os.environ.get("TMPDIR", "/tmp"), "pereezd-sha-cache.json")
SAVE_SCRIPT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "skills", "pereezd", "scripts", "save-file.sh"))


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


def sha12(path, cache):
    st = os.stat(path)
    key = f"{path}|{st.st_size}|{int(st.st_mtime)}"
    if key in cache:
        return cache[key], 0
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    cache[key] = h.hexdigest()[:12]
    return cache[key], st.st_size


def unsaved_uploads(registry):
    """Файлы из папок загрузок, которых нет в реестре (по sha256, большие по имени)."""
    try:
        with open(CACHE) as f:
            cache = json.load(f)
    except Exception:
        cache = {}
    cached = {k.rsplit("|", 2)[0] for k in cache}
    out, budget, fresh_cache = [], HASH_BUDGET, {}
    for d in UPLOAD_DIRS.split(":"):
        if not d or not os.path.isdir(d):
            continue
        for base, _, names in os.walk(d):
            for n in names:
                fp = os.path.join(base, n)
                try:
                    size = os.path.getsize(fp)
                    if size <= HASH_LIMIT and (budget > 0 or fp in cached):
                        s12, spent = sha12(fp, cache)
                        budget -= spent
                        st = os.stat(fp)
                        k = f"{fp}|{st.st_size}|{int(st.st_mtime)}"
                        fresh_cache[k] = cache[k]
                        known = f"| {s12} |" in registry
                    else:
                        name = re.escape(n.replace(" ", "_").replace("|", "_"))
                        known = re.search(rf"(^|[-/ ]){name}[`) ]", registry, re.M) is not None
                except OSError:
                    continue
                if not known:
                    out.append(fp)
                if len(out) >= 20:
                    break
            if len(out) >= 20:
                break
        if len(out) >= 20:
            break
    try:
        with open(CACHE, "w") as f:
            json.dump(fresh_cache, f)
    except Exception:
        pass
    return out


def dirty_files(root):
    """Файлы реестра, которые не закоммичены или не запушены: пропадут с контейнером."""
    def git(*args):
        return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, timeout=2)
    try:
        if git("status", "--porcelain", "--", "sessions/files").stdout.strip():
            return True
        r = git("log", "--oneline", "@{u}..HEAD", "--", "sessions/files")
        if r.returncode != 0:  # нет upstream: ветка не запушена целиком
            return bool(git("log", "--oneline", "-1", "--", "sessions/files").stdout.strip())
        return bool(r.stdout.strip())
    except Exception:
        return False


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
            + f". Сохрани их в этом же ходе: bash \"{SAVE_SCRIPT}\" <файл> \"<суть>\". "
            "ПДн, цены, договоры в публичный репозиторий не класть: для них --link <ссылка на "
            "приватное хранилище>. Иначе следующая сессия попросит файлы повторно."
        )
    if registry and dirty_files(root):
        notes.append(
            "[pereezd] В sessions/files есть незакоммиченное или незапушенное: закоммить и запушь, "
            "контейнер одноразовый."
        )
    if new_session and registry:
        count = sum(1 for line in registry.splitlines() if line.startswith("| ") and "sha256" not in line)
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
