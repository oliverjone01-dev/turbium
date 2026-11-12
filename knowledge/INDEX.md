# Карта репозитория TURBIUM

Одна строка на место. Сначала найди здесь, потом открывай. Целиком большие файлы не читать.

## Знания
- `knowledge/decisions.md` - журнал решений с датами. Решённое не пересматривать
- `knowledge/facts.md` - реестр проверенных цифр: источник и тег
- `sessions/handoff/` - передаточные файлы переездов между сессиями, `_TEMPLATE.md` - шаблон

## Бренд и сайт
- `site/index.html` - Visual DNA и платформа бренда (источник правды), `site/build-locked.mjs` - сборка под паролем
- `strategy/` - стратегия, та же схема сборки под паролем
- `www/` - публичный сайт, `m1-fix/` - правки сайта m1 со сборкой `build.py`

## Исследования
- `research/` - единое исследование МСБ, сводная верификация, JTBD, сырые выгрузки `2026-07-*-raw.md`

## Контент
- `content/plan/turbium-content-plan-26w.xlsx` - контент-план 26 недель, генератор `build-plan.mjs`
- `content/TURBIUM_Carousel_Factory_System.docx` - контент-фабрика
- `content/` - launch plan, мастер-промпты, планы каруселей и постов
- `references/` - эталонная карусель и визуальные референсы

## Производство
- `production/TZ_01..06` - ТЗ: карусели, shorts, фото, brand OS, сайт m1, дизайн и UX
- `production/PROMPT_*`, `RENDER_PROMPTS_*` - промпты сборки сайта и рендеров

## Аудиты
- `audit/` - отчёты ФЕНИКСА (история, не переписывать), `audit-report.json` - формат отчёта

## Агенты и скиллы
- `.claude/agents/` - ростер: feniks, spartak и команда (таблица в CLAUDE.md)
- `.claude/skills/` - скиллы проекта, `.claude/commands/` - команды (`/council`, `/crisis`, `/pereezd`)
