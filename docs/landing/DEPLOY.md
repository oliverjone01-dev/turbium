# TURBIUM: публикация и перенос на VPS

Публичное демо: https://oliverjone01-dev.github.io/turbium/landing/

Статический лендинг v3: HTML, CSS, JavaScript, WebGL. Для работы не нужны Node.js, база данных, ключи API или сборщик. Изображения, шрифты и скрипты находятся в репозитории. Данные в интерфейсе учебные; заявка пока копируется, а не отправляется.

## 1. Быстрый запуск на VPS по IP

Нужны Git и Docker Engine с Compose v2. Установка Docker по инструкции для вашей ОС: https://docs.docker.com/engine/install/ . Команды выполняйте по SSH на VPS пользователем с доступом к Docker.

```sh
git clone https://github.com/oliverjone01-dev/turbium.git
cd turbium
docker compose up -d
docker compose ps
```

Откройте `http://IP_ВАШЕГО_VPS:8080` на компьютере или телефоне. В панели провайдера и firewall VPS разрешите входящий TCP 8080. Если порт занят: `PORT=8090 docker compose up -d`; используйте тот же PORT при следующих командах. HTTP подходит для просмотра демо. Для рабочего домена используйте HTTPS ниже.

## 2. Домен и автоматический HTTPS

Создайте A-запись домена на IPv4 VPS. Если есть AAAA, она должна указывать на рабочий IPv6 этого же сервера. Откройте TCP 80/443; UDP 443 необязателен (HTTP/3). Эти порты должны быть свободны. Если на VPS уже работает nginx, панель хостинга или другой сайт, используйте вариант 3.

```sh
cp .env.example .env
nano .env
```

Замените `DOMAIN=landing.example.com` на ваш реальный домен без `https://` и без пути. Затем:

```sh
docker compose down
docker compose -f compose.vps.yaml config --quiet
docker compose -f compose.vps.yaml up -d
docker compose -f compose.vps.yaml ps
docker compose -f compose.vps.yaml logs --tail=80 web
```

Откройте `https://ВАШ_ДОМЕН`. Caddy получает и продлевает сертификат автоматически, если DNS и доступ к портам настроены. Выпуск сертификата может занять несколько минут. Сертификаты хранятся в постоянном Docker volume `caddy_data`: при обычном обновлении он сохраняется. Не запускайте `down -v`, если хотите сохранить сертификаты.

## 3. VPS с существующим nginx или панелью

```sh
BIND_ADDRESS=127.0.0.1 PORT=8080 docker compose up -d
```

Настройте существующий HTTPS reverse proxy на `http://127.0.0.1:8080`. Не запускайте `compose.vps.yaml`, чтобы не занять чужие 80/443. Значения BIND_ADDRESS и PORT удобно сохранить в `.env` для последующих запусков. Альтернатива без Docker: скопируйте только содержимое `www/landing/` в document root сайта. Сайт корректно работает в корне и в подпапке.

## 4. Обновление и откат

Обновление файлов из GitHub:

```sh
git pull --ff-only
docker compose -f compose.vps.yaml up -d
```

Для preview используйте `docker compose up -d`. Статика подключена как read-only volume и обновляется после pull. Если изменяли Caddyfile, перезапустите только контейнер: `docker compose -f compose.vps.yaml restart web`. Для явного обновления базового образа выполните `docker compose -f compose.vps.yaml pull` перед `up -d`. Тег образа `caddy:2-alpine`; перед обновлением проверьте примечания Caddy.

Перед обновлением можно записать версию: `git rev-parse HEAD`. Для отката выберите прошлый SHA из `git log`, выполните `git switch --detach SHA` при чистой рабочей копии и перезапустите контейнер. Возврат на актуальную ветку: `git switch main`, затем `git pull --ff-only`. Локальный `.env` игнорируется Git.

## 5. GitHub Pages

В этом репозитории уже действует `.github/workflows/pages.yml`: изменения `www/**` в main публикуются в gh-pages. Новая сборка находится в `www/landing/`. Остальные публичные маршруты и запароленные платформы сохраняются. Изменять настройки Pages не требуется. Проверка публикации: вкладка Actions, затем публичный URL.

## 6. WordPress

Установите `packages/turbium-landing-wordpress.zip` через «Плагины → Добавить → Загрузить». Создайте страницу без шапки и подвала темы, добавьте shortcode `[turbium_landing]`. Это отдельный способ установки; контейнер Caddy запускает статическое демо и не устанавливает WordPress.

Исходник фрагмента: `wordpress/page.html`; PHP: `wordpress/turbium-landing.php`; общие ресурсы: `www/landing/assets/`. После изменения фрагмента/ассетов выполните `python3 scripts/build-landing.py`: команда обновляет публичный HTML и ZIP.

## 7. Локальная проверка

```sh
python3 scripts/check-landing.py
node --check www/landing/assets/app.js
python3 -m http.server 8080 --directory www/landing
```

Страница адаптируется к компьютерам, планшетам и телефонам. При недоступном WebGL предусмотрен Canvas fallback, при reduced-motion анимация приостанавливается. Это не обещание одинакового FPS на всех устройствах. В текущем окружении проверен встроенный браузер desktop/mobile; реальный VPS и весь парк Safari/Firefox/Android отдельно не тестировались.

## Документация серверной части

- Caddy + Docker Compose: https://caddyserver.com/docs/running#docker-compose
- Автоматический HTTPS: https://caddyserver.com/docs/automatic-https
- Исходники изображений и методика демо: [README.txt](README.txt)
