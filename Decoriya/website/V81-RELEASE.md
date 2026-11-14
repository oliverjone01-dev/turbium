# ДЕКОРИЯ 8.1 — GitHub Pages
Источник: Figma SsbOVLwLJnNFPwaeQ3bRqJ, страница 174:409.
17 секций desktop/mobile; экспорт восстановлен редактируемым HTML/CSS. Сохранены фирменные портрет/руки/стол и новогодние сцены, галерея, палитры, селекторы, памятка и FAQ.
Страницы кейсов: projects/myata-lounge/ и projects/britva/. Бриф хранит case_id, название и URL через проверку/редактирование. Нет предвыбранных типа бизнеса и даты.
По указанию владельца канал отправки оставлен пустым. #open-manager href="" и aria-disabled="true". Сайт не сообщает об отправке; можно скопировать бриф. До подключения и проверки получателя этот релиз не подтверждает получение заявки менеджером.
SEO: canonical на фактическом GitHub Pages URL, заголовки и description по страницам, Open Graph, Organization/WebSite/Service и breadcrumbs на кейсах, sitemap.xml, robots.txt по /turbium/robots.txt через workflow (корень публикации проекта, не корень общего хоста). При переезде заменить origin во всех метаданных и карте. У oliverjone01-dev.github.io/robots.txt сейчас 404; управление корнем этого хоста относится к отдельному репозиторию. Это не запрет обхода. Sitemap нужно отправить через подтверждённый Search Console / Вебмастер; на собственном домене разместить robots.txt в корне хоста.
Runtime: v81.css, v81-site.css, v81.js, cases.json, assets/v81. Исходные прежние JS/CSS и WordPress-архивы оставлены для истории, index.html их не подключает. Старый WordPress-пакет не является релизом 8.1.
Проверки: python3 tools/check-v81.py; node --check v81.js.
