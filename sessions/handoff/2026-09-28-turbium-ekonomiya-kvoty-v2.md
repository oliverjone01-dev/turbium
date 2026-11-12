# TURBIUM - Экономия квоты - v2

- **Дата:** 2026-09-28
- **Прошлая сессия:** https://claude.ai/code/session_01Fzz5HjC7LBwRXuKQ5ua68s («TURBIUM - Экономия квоты - v2»)
- **Прошлый handoff:** sessions/handoff/2026-09-28-turbium-ekonomiya-kvoty-v1.md (цель, решения, факты, грабли оттуда в силе)
- **Ветка:** `claude/loving-fermi-u64ugn` в обоих репозиториях (turbium и t1)

## 1. Цель
Сократить слив квоты без потери качества: короткие сессии с автопереездом, чистый набор скиллов, знания в `knowledge/`. «Готово» = turbium#2 и t1#421 смержены, датчик и переезд работают, плагин pereezd раздаётся коллегам.

## 2. Сделано в v2
- Плагин `pereezd` для коллег (просьба пользователя: «упакуй, чтобы разворачивать у коллег в Claude Code и Cowork»): turbium `plugins/pereezd/` (скилл в переносимой версии с режимами Git/Папка/Чат и встроенным шаблоном, `/pereezd`, датчик-хук через `${CLAUDE_PLUGIN_ROOT}`, README, `build.sh`, `dist/*.zip`) + каталог `.claude-plugin/marketplace.json`. Коммиты `dabf4df`, `421ebc9`. Архивы отправлены пользователю.
- t1 подключён (add_repo push, клон `/home/user/t1` - в новой сессии клонировать заново), подписки на turbium#2 и t1#421 оформлены.
- ФЕНИКС-аудит t1#421 (`ce0617f`): **7.4/10, RETURN, вето нет, блокеров нет.** Сверка CLAUDE.md: 186 строк дословно + 10 с заменой ссылок на удалённые скиллы, ни один порог/запрет/HITL не потерян. Хук-тесты 112/112, smoke-test OK, sync-agents синхрон, висячих путей на удалённые скиллы нет, em dash 0, цен и ПДн нет.

## 3. Решения и почему
- Решения v1 в силе (удаление скиллов не возвращать, feniks и ростер Спартака остаются, векторной базы нет, правила чек-инов).
- Основной способ раздачи плагина - архив в claude.ai (Customize -> Plugins -> Upload): по докам попадает в Cowork и Claude Code аккаунта, хуки работают в Cowork и Claude Code, не в чате. Каталог `/plugin marketplace add oliverjone01-dev/turbium` - второй путь (нужен доступ к репо).
- В turbium и t1 плагин не ставить: датчик уже подключён в проекте, подсказка задвоится.

## 4. Факты и цифры
- CI: на turbium#2 и t1#421 проверок 0 (get_status/get_check_runs 28.09) - [ДАННЫЕ]. CI в репо не настроен, ждать нечего.
- Новый CLAUDE.md t1: 5261 знак - замер ФЕНИКСА - [ДАННЫЕ].

## 5. Карта файлов
- turbium: `plugins/pereezd/**`, `.claude-plugin/marketplace.json`, этот файл.
- t1 (правки ниже): `CLAUDE.md`, `knowledge/os/{gates,protocols,routing,environments}.md`, `knowledge/{decisions,facts}.md`, `.claude/settings.json`, `.claude/hooks/{p9-trigger-detector,deliver-gate,anti-slop-checker}.sh`, `.claude/hooks/tests/run-hook-tests.sh`, `.claude/skills/pereezd/SKILL.md`.

## 6. Грабли
- Автоматический режим отклоняет add_repo и subscribe_pr_activity без прямого слова пользователя. Правку `.claude/` и CLAUDE.md тоже может отклонить: тогда спросить пользователя одной строкой с перечнем файлов.
- t1 публичный: никаких цен, ПДн, токенов.

## 7. Открыто - замечания ФЕНИКСА к t1#421 (сделать все)
Важно:
1. Хуки ссылаются на разделы, которых нет в новом CLAUDE.md: `p9-trigger-detector.sh:47` «CLAUDE.md §5» -> `knowledge/os/gates.md §5`; `deliver-gate.sh:72` «CLAUDE.md §4» -> «CLAUDE.md, Step 12.5 (подробно knowledge/os/gates.md §4)»; `anti-slop-checker.sh:3,42,76` «CLAUDE.md §7» -> `knowledge/os/style.md §7`.
2. ~20 живых ссылок «CLAUDE.md §N» в agents/*, .claude/agents/* (зеркала, после правки `sync-agents.sh`), skills/{council,geo-aeo,roster-protocol,humanizer-ru}, .impeccable.md, yd-api-write.sh:55, kontur-dashboard, .github/workflows/ym-snapshots.yml:238. Минимум: строка в CLAUDE.md перед роутингом «Ссылки вида "CLAUDE.md §N" ведут в knowledge/os/ по номерам ниже». Лучше массовая замена скриптом.
3. В CLAUDE.md после строки 26 (Step 12.5) вернуть: «К запросу ФЕНИКСУ приложить self-check 25 пунктов (knowledge/feniks/eval-checklist.md), без него return без скоринга». В строку 62 про P9: одна строка со списком триггеров (финансовые слова, план/инициатива, розовые очки, чужие кейсы, диапазон >2x; полный список gates.md §5).
4. **Баг:** `.claude/settings.json:74` при пустом CLAUDE_PROJECT_DIR python3 выходит с rc=2 = блок промпта. -> `python3 "${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/context-meter.py"`. То же проверить в turbium `.claude/settings.json`.
5. pereezd SKILL.md:34 (t1, и то же в turbium `.claude/skills/pereezd` и `plugins/pereezd`): пушить только в рабочую не-main ветку; критический артефакт без вердикта ФЕНИКСА - пометка «аудит не пройден» в handoff и WIP в коммите.
Мелочи: 6) gates.md:37-38 слить дубль про разметку data; 7) p9-детектор:47 убрать дубль RU/EN; 8) protocols.md:43-45 `gengroup-content-factory` + «(версия claude.ai)»; 9) шапки knowledge/os/*: «дословно, кроме ссылок на удалённые скиллы»; 10) шапка gates.md: «при расхождении действует CLAUDE.md»; 11) CLAUDE.md:63 «Не использовать длинное тире (U+2014)»; 12) knowledge/decisions.md:5-6 цифры 50-85% и 695 - тег [ГИПОТЕЗА] или источник; 13) knowledge/facts.md «16 000 м²» -> [ГИПОТЕЗА] до первички; 14) тесты context-meter в run-hook-tests.sh (<150K молчит, >=200K ОБЯЗАТЕЛЕН, битый JSON rc=0).
- Описание PR t1#421: поправить «сверка 196/196» на «186 дословно + 10 с заменой ссылок».
- `content/plan/turbium-content-plan-26w.xlsx` не пересобран (из v1).

## 8. Следующий шаг
Склонировать t1 (ветка claude/loving-fermi-u64ugn), внести правки 1-14 раздела «Открыто», прогнать `.claude/hooks/tests/run-hook-tests.sh`, `schemas/smoke-test.py`, `sync-agents.sh --check`, json.tool, запушить; пункты 4-5 перенести в turbium (`.claude/` и `plugins/pereezd`, пересобрать `build.sh`). Затем повторный прогон агента feniks, цель ≥8, и вердикт пользователю.

## 9. Фон
- Открытые PR: turbium#2, t1#421 - подписаться. В v2 подписки сняты при переезде.
- Чек-инов в v2 не ставилось.
- Рутины пользователя (Ozon 09:00 UTC, сторож 09:30 UTC, контент-цикл по пятницам) не трогать.

## 10. Как пользователь любит работать
- Коротко, прямые вердикты в стиле ФЕНИКСА с цифрами и тегами.
- Автоматизация без лишних вопросов; разрешения даёт одной фразой («подключить t1 и подписаться на PR»).
- Русский, только дефис.
