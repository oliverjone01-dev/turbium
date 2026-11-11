/* Shared runtime timings and implementation map. */
window.DK_MOTION=Object.freeze({
  "version": "6.4.1",
  "easing": "cubic-bezier(.16,1,.3,1)",
  "control": 250,
  "reveal": 720,
  "stagger": 90,
  "hero": {
    "background": 1200,
    "header": 640,
    "headerDelay": 120,
    "title": 900,
    "titleDelay": 200,
    "person": 1100,
    "personDelay": 240,
    "backgroundScroll": 45,
    "backgroundPointer": 44,
    "pointerVertical": 24,
    "tilt": 1.4
  },
  "parallax": {
    "material": 105,
    "mobile": 36
  },
  "gallery": {
    "filter": 420,
    "image": 250,
    "indicator": 250,
    "cursor": 84,
    "dragThreshold": 6
  },
  "blocks": [
    {
      "id": "header",
      "selector": ".header",
      "trigger": "DOMContentLoaded; scrollY > 80",
      "effect": "Шапка без рамки и карточной подложки; появление сверху и компактный режим по прокрутке.",
      "desktop": "96 → 60 px. На hero — прозрачный световой градиент для читаемости; при прокрутке ivory на всю ширину.",
      "mobile": "76 → 50 px; меню 44 px.",
      "reduced": "Сразу видима, без движения и плавного изменения.",
      "source": "motion.js: entrance(), updateScroll(); spatial.css: .header"
    },
    {
      "id": "hero-background",
      "selector": ".hero-backdrop",
      "trigger": "Загрузка hero; прокрутка и движение мыши в hero",
      "effect": "Спокойная светлая студия декора. Рабочая зона и люди только в глубине справа; чистая стена за текстом.",
      "desktop": "Указатель до ±44 px по X и ±24 px по Y, наклон ±1,4°. Плавное догоняющее движение через rAF. Скролл до 45 px.",
      "mobile": "На ширине ≤1100 px комната статична.",
      "reduced": "Статичный фон.",
      "source": "motion.js: room, updateScroll(), pointer handler; spatial.css: .hero-backdrop"
    },
    {
      "id": "hero-title",
      "selector": ".title-mask > span",
      "trigger": "DOMContentLoaded",
      "effect": "Три строки выходят из масок снизу, без искажения букв",
      "desktop": "900 мс, старт 200 мс, шаг 90 мс.",
      "mobile": "Та же последовательность, крупный адаптивный текст.",
      "reduced": "Текст сразу виден.",
      "source": "motion.js: entrance()"
    },
    {
      "id": "hero-person",
      "selector": ".hero-anchor",
      "trigger": "DOMContentLoaded",
      "effect": "Прежнее лицо и верх портрета. Отдельная ретушь кистей и целой манжеты, мягкое совмещение ниже груди и контактная тень на непрерывном столе.",
      "desktop": "1100 мс, задержка 240 мс. Лицо не анимируется отдельно; стол не уплывает от рук.",
      "mobile": "Та же единая сцена, полностью видимое лицо, стол выходит до края экрана.",
      "reduced": "Портрет сразу виден.",
      "source": "motion.js: entrance(); spatial.css: .hero-anchor, .hero-hands"
    },
    {
      "id": "hero-byline",
      "selector": ".hero-byline",
      "trigger": "DOMContentLoaded",
      "effect": "Чистая типографическая подпись имени и роли без имитации автографа.",
      "desktop": "700 мс, задержка 850 мс, сдвиг 12 px.",
      "mobile": "Имя под сценой; та же спокойная последовательность.",
      "reduced": "Сразу видимое имя.",
      "source": "motion.js: entrance(); spatial.css: .hero-byline"
    },
    {
      "id": "works",
      "selector": "#works-rail",
      "trigger": "Drag мышью; свайп; стрелки; фокус/клавиатура",
      "effect": "Галерея со scroll snap, настоящей кнопкой «Листать», drag без native anchor drag и открытием фото.",
      "desktop": "Кнопка «Листать» остаётся справа у ленты и переводит к следующему кадру. Drag мышью от 6 px; обычный клик открывает фото.",
      "mobile": "Нативный свайп и кнопки 44 px; без drag-курсора.",
      "reduced": "Прокрутка мгновенная, без декоративных перемещений.",
      "source": "app.js: setupRail(), openViewer()"
    },
    {
      "id": "services",
      "selector": "[data-spatial] .sequence-canvas",
      "trigger": "Hover мышью; фокус клавиатуры; клик/тап; Escape",
      "effect": "48 настоящих ракурсов каждой из трёх 3D-сцен. Камера проходит 30° по горизонтали и поднимается на 12°. Раскрытие 1 — свет, 2 — декор, 3 — поверхности, в левую сторону.",
      "desktop": "1800 мс. Worker декодирует небольшие части вне основного потока; Canvas смешивает соседние готовые кадры; геометрия каждого кадра отрендерена в Blender. Обратное воспроизведение с текущей позиции.",
      "mobile": "Тап открывает, повторный собирает. Мобильные части по восемь кадров 384×288; загружается по взаимодействию. Canvas работает только во время перехода.",
      "reduced": "Мгновенное переключение двух статичных ракурсов; атлас не запрашивается.",
      "source": "tools/render-camera-v64.py; assets/camera-v64; motion.js:setupSpatial; motion-config.js:spatial"
    },
    {
      "id": "directions",
      "selector": "#ideas-rail; .gallery-filters",
      "trigger": "Выбор фильтра; горизонтальный просмотр",
      "effect": "15 направлений без повторных бейджей. Каждый кадр имеет индивидуальный редакционный текст.",
      "desktop": "Фильтр 420 мс, индикатор 250 мс. Auto-play отсутствует.",
      "mobile": "Свайп и кнопки; плашка учитывает перенос строки.",
      "reduced": "Мгновенная смена набора и плашки.",
      "source": "app.js: filterIdeas(), updateIndicator()"
    },
    {
      "id": "manifesto",
      "selector": "main h2; [data-editorial-reveal]",
      "trigger": "Первый вход заголовка/манифеста в viewport",
      "effect": "Слова выходят из отдельных масок, последовательно выпрямляются и набирают непрозрачность.",
      "desktop": "820 мс, шаг 32 мс, максимальная задержка 420 мс; без мерцания и расшифровки букв.",
      "mobile": "Та же последовательность с естественным переносом строк.",
      "reduced": "Полностью видимый текст, без масок движения.",
      "source": "motion.js: setupEditorial(), revealWords(); spatial.css: .editorial-word-mask"
    },
    {
      "id": "materials",
      "selector": ".material-photo picture",
      "trigger": "Прокрутка через блок материалов",
      "effect": "Расширенный кадр с большим запасом фона. Параллакс до ±105 px; края изображения остаются за рамкой.",
      "desktop": "Кадр +240 px по высоте, верхний запас 120 px, перемещение до 105 px.",
      "mobile": "Запас 60 px сверху и снизу, перемещение до 36 px.",
      "reduced": "Статичный кадр.",
      "source": "motion.js: updateScroll(); spatial.css: .material-photo"
    },
    {
      "id": "expert-process",
      "selector": "#olesya .reveal; .steps",
      "trigger": "Вход в viewport и прокрутка этапов",
      "effect": "Три фирменные иконки этапов прорисовываются при входе. Детали реагируют на hover; линия следует прогрессу.",
      "desktop": "Штрихи 900 мс, детали 650 мс. Иконки: обсуждение, концепция, монтаж.",
      "mobile": "Статичный рисунок после одного появления; этапы вертикальны.",
      "reduced": "Все элементы статичны.",
      "source": "motion.js: drawIcon(), observeReveals(), updateScroll(); assets/spatial/icon-*.svg"
    },
    {
      "id": "contact-footer",
      "selector": "#contact; [data-magnetic]; .footer",
      "trigger": "Viewport; mousemove над основным CTA",
      "effect": "Появление заголовка и небольшой отклик CTA для мыши. Один компактный логотип в подвале.",
      "desktop": "Только указатель мыши, без непрерывного мерцания.",
      "mobile": "Статичный CTA; фиксированная кнопка скрывается при видимом основном действии.",
      "reduced": "Обычные кнопки, без движения.",
      "source": "motion.js: setupMagnetic(); app.js: visibility observers"
    },
    {
      "id": "viewer-menu",
      "selector": "#gallery-viewer; #mobile-menu",
      "trigger": "Клик/Enter; Escape; стрелки; смена исходника",
      "effect": "Модальные поверхности, кроссфейд фотографии, миниатюры; исходник/обработка для реальных кадров",
      "desktop": "Изображение 250 мс. Фокус удерживает native dialog, закрытие возвращает его карточке.",
      "mobile": "Фото свайпается; закрытие и переключатель доступны; вертикальная прокрутка.",
      "reduced": "Мгновенная смена без кроссфейда.",
      "source": "app.js: openViewer(), renderViewer(), close handlers"
    },
    {
      "id": "contact-pattern",
      "selector": ".contact-pattern",
      "trigger": "IntersectionObserver: секция видна не менее чем на 15%",
      "effect": "Мягкий блик проявляет авторские векторные контуры ткани на бордовом фоне. Контент остаётся выше паттерна.",
      "desktop": "Цикл 11 с, opacity 0.035–0.12. Градиентная маска проходит только по линиям. Вне viewport анимация приостановлена.",
      "mobile": "Та же спокойная световая пластика, без захвата прокрутки и указателя.",
      "reduced": "Статичный паттерн opacity .035, без движения.",
      "source": "assets/studio/atelier-ribbon-pattern.svg; spatial.css: @keyframes atelier-light; motion.js: boot()"
    }
  ],
  "editorial": {
    "duration": 820,
    "stagger": 32,
    "maxDelay": 420
  },
  "icons": {
    "duration": 900
  },
  "spatial": {
    "renderer": "Blender48-frame-camera-sequence",
    "duration": 1800,
    "frames": 48,
    "columns": 4,
    "stripFrames": 8,
    "rows": 2,
    "cameraOrbitDegrees": 30,
    "cameraElevationDegrees": 12,
    "order": [
      "light",
      "decor",
      "surfaces"
    ],
    "stages": {
      "light": [
        0.06,
        0.46
      ],
      "decor": [
        0.27,
        0.76
      ],
      "surfaces": [
        0.53,
        0.96
      ]
    },
    "direction": "Light and decor move to screen-left; architectural assembly moves right.",
    "frameBlend": "Premultiplied additive blend of adjacent rendered samples. No CSS perspective warp."
  }
});
