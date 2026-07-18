# GCONF: от сигнала к проверяемому контенту

Этот репозиторий — work sample для роли **AI-first content & growth generalist** в GCONF и одновременно прототип локальной AI-first редакции.

Его задача — показать не только финальные посты, но и воспроизводимый путь от живого сигнала до публикации:

> источники → нормализация → evidence base → редакционное решение → текст → дизайн/форматирование → ручная публикация → обратная связь

Система собирает публичные материалы GCONF и свежие сигналы об AI, сохраняет происхождение каждого значимого утверждения и использует специализированные AI-агенты для отдельных этапов работы. Там, где требуется вкус, разрешение на публикацию или коммерческое решение, процесс останавливается и ждёт человека.

Итоговая презентация work sample находится в [`submission-site/`](submission-site/). Готовые примеры анонса — в [`GCONF announce 2026-10-27/`](GCONF%20announce%202026-10-27/), примеры новостей для ручной публикации — в [`Telegram, News to publish/`](Telegram%2C%20News%20to%20publish/).

## Что лежит в репозитории

```text
gconf/
├── telegram/                    # исходные экспорты Telegram
├── Instagram/                   # исходные экспорты Instagram и визуальные референсы
├── YouTube/                     # нормализованные исследовательские пакеты видео
├── Web Articles/                # локальные снимки статей официальных AI-лабораторий
├── knowledge/                   # Obsidian knowledge base и служебное состояние
│   ├── _index/gconf.sqlite      # готовый к поиску и полностью пересобираемый SQLite snapshot
│   ├── sources/                 # сгенерированные карточки источников
│   ├── pains/, cases/, ...      # смысловые карточки с evidence locators
│   ├── processing/              # состояние semantic extraction
│   └── editorial/               # журнал человеческих решений и гейтов
├── research/                    # анализы, writer runs и другие редакционные артефакты
├── editorial/                   # канонический tone of voice GCONF
├── .agents/skills/              # локальные специализированные агенты и их CLI
├── submission-site/             # статическая презентация результата
├── GCONF announce 2026-10-27/   # собранный анонс и Instagram-карусель
├── Telegram, News to publish/   # форматированные handoff-копии, не факт публикации
└── AGENTS.md                     # полные правила проекта для AI-агентов
```

### 1. Raw / source data

Исходные материалы находятся в [`telegram/`](telegram/), [`Instagram/`](Instagram/), [`YouTube/`](YouTube/) и [`Web Articles/`](Web%20Articles/). Это первичный слой доказательств: импортёр читает его, но не переписывает.

- `telegram/*.json` — публичные каналы, GCONF-сообщество и исторические обсуждения;
- `Instagram/*.json` — посты, комментарии, метрики и структура каруселей;
- `YouTube/<creator>/<video>/` — метаданные, снимок статистики, комментарии, описание, главы, субтитры или транскрипт;
- `Web Articles/<Lab>/<article>/<snapshot>/` — полный нормализованный текст официальной публикации, метаданные и checksum;
- отдельные локальные исследовательские материалы могут находиться в `research/` и также попадать в индекс.

Публичные метрики и доступность страниц меняются со временем, поэтому у снимков сохраняются дата сбора, URL и ограничения полноты. Сводка текущих пакетов доступна командой `scan` из раздела «Быстрый старт».

### 2. SQLite: машинный поисковый индекс

[`knowledge/_index/gconf.sqlite`](knowledge/_index/gconf.sqlite) — производный индекс всех локальных источников. Он содержит нормализованные документы, комментарии, фрагменты транскриптов, связи ответов, checksums, provenance и полнотекстовый поиск FTS5.

В Git хранится готовый snapshot, чтобы после clone можно было сразу проверять корпус и выполнять поиск. При этом SQLite — **не источник истины** и не редактируется вручную: его можно целиком пересобрать из raw-артефактов. После изменения источников snapshot нужно обновить через ingestion и закоммитить вместе с ними. Отчёты каждого импорта пишутся в `knowledge/runs/`, а обзорные карточки источников — в `knowledge/sources/`.

### 3. Knowledge base: проверяемый смысловой слой

Папку [`knowledge/`](knowledge/) можно открыть как Obsidian vault. В ней хранятся смысловые карточки типов:

- `actors` — люди и организации;
- `cohorts` — когорты и события GCONF;
- `pains` — напряжения и боли аудитории;
- `cases` — кейсы и наблюдаемые результаты;
- `trends` — повторяющиеся изменения;
- `technologies` и `labs` — технологии и AI-лаборатории;
- `claims` — проверяемые утверждения.

Каждая карточка различает `fact`, `inference` и `proposal`, содержит точные ссылки на evidence и имеет отдельный `review_status`. Карточка `candidate` означает «агент нашёл возможный смысл», а не «человек подтвердил его».

Важно различать три слоя:

| Слой | Для чего нужен | Можно ли считать редакционной истиной |
|---|---|---|
| Raw-артефакты | первичные доказательства | да, с учётом происхождения и свежести |
| SQLite и `knowledge/sources/` | быстрый поиск и навигация | нет, это пересобираемый индекс |
| Проверенные semantic cards | повторно используемая evidence-backed knowledge base | да, только после human review |

### 4. Research и публичные результаты

[`research/`](research/) хранит воспроизводимые запуски редакционных этапов, а не одну бесконечно перезаписываемую черновую папку:

- `announcement_analysis/runs/` — анализ аудитории и варианты направления анонса;
- `announcement_drafts/runs/` — тексты после человеческого выбора направления;
- `news_analysis/runs/` — радар и приоритизированный backlog тем;
- `news_drafts/runs/` — новости по явно выбранным человеком topic ID;
- `instagram_carousels/runs/` — исходники и проверенные изображения каруселей;
- `tone_of_voice/` и `gconf_history/` — исследования голоса и истории GCONF.

Отформатированный файл в `Telegram, News to publish/` — это handoff для ручной публикации, а не свидетельство, что пост опубликован.

## Как устроен полный loop

```text
живой сигнал / идея
        ↓
сбор локального source package
        ↓
детерминированный ingestion → SQLite + source cards
        ↓
semantic extraction → candidate cards
        ↓
человеческая проверка knowledge base
        ↓
┌──────────────────────────────┬────────────────────────────────┐
│ NEWS                         │ ANNOUNCEMENT                   │
│ radar → выбор topic ID       │ analysis → выбор направления  │
│ → freshness check → writer  │ → facts/CTA allowlist → writer│
└──────────────────────────────┴────────────────────────────────┘
        ↓
человеческое одобрение текста и permissions
        ↓
Telegram formatting / Instagram design
        ↓
человеческое одобрение финального артефакта
        ↓
ручная публикация
        ↓
сигналы: внимание → клик → ответ → заявка → оплата → доверие
        ↺ следующий цикл отбора и улучшения
```

### Откуда берётся идея

Идея может прийти из свежего релиза AI-лаборатории, обсуждения в комментариях, кейса участника, повторяющегося вопроса аудитории или изменения в поведении пользователей. Агент сопоставляет сигнал с локальной историей GCONF: публиковалась ли уже эта мысль, есть ли реальная новая дельта, кому она полезна сейчас и к какому действию может привести.

### Ветка новостей

1. `gconf-news-radar` просматривает свежие публичные сигналы и все обязательные локальные source lanes.
2. Он дедуплицирует события, проверяет прошлое покрытие GCONF, оценивает темы и создаёт backlog — **без написания постов**.
3. Человек выбирает конкретные `topic_id`; решение фиксируется в append-only editorial gate.
4. `gconf-news-writer` повторно открывает первоисточники, проверяет свежесть центрального факта и пишет reviewable draft.
5. После одобрения текста и прав `gconf-telegram-formatter` создаёт чистую публикационную копию.
6. Человек публикует её вручную и возвращает реакцию аудитории в следующий цикл.

### Ветка анонса

1. `gconf-announcement-analysis` соединяет knowledge base, историю анонсов, текущую страницу `gconf.io`, voice standard и свежие AI-сигналы.
2. Он предлагает 2–3 направления и объясняет evidence — **без выбора победителя и без публичного копирайтинга**.
3. Человек выбирает направление и отдельно подтверждает допустимые факты, CTA, цитаты и разрешения.
4. `gconf-announcement-writer` создаёт Telegram-текст и ровно шесть Instagram-слайдов с caption.
5. После copy approval `gconf-instagram-carousel-designer` собирает и валидирует изображения, а `gconf-telegram-formatter` готовит Telegram-handoff.
6. Финальные изображения и текст утверждает и публикует человек.

### Почему процесс не полностью автоматический

Агенты хорошо собирают контекст, ищут повторы, проверяют структуру артефактов и сохраняют трассируемость. Но они не должны самостоятельно:

- объявлять candidate-карточку подтверждённым знанием;
- выбирать стратегию запуска или тему только потому, что она выше в рейтинге;
- придумывать даты, цены, программу, результаты или разрешения на цитирование;
- подменять изменившийся инфоповод похожей новостью;
- утверждать публичный текст, визуал или коммерческий CTA;
- публиковать контент.

Эти решения фиксируются как append-only карточки в `knowledge/editorial/`: новое решение может заменить старое через `supersedes`, но не стирает историю.

## Локальные skills: кто за что отвечает

Skills в [`.agents/skills/`](.agents/skills/) — это не один универсальный «контент-бот», а набор агентов с узкими входами, выходами и запретами.

| Skill | Роль |
|---|---|
| `gconf-youtube-research` | собирает полный локальный пакет одного YouTube-видео |
| `gconf-yt-dlp` | низкоуровневая диагностика URL, метаданных и субтитров |
| `gconf-local-whisper` | локально транскрибирует файл, если готовых субтитров нет |
| `gconf-knowledge-ingest` | детерминированно импортирует уже собранные источники в SQLite |
| `gconf-insight-extract` | создаёт трассируемые semantic candidates из проиндексированного evidence |
| `gconf-editorial-gates` | фиксирует человеческие выборы, approvals и permissions |
| `gconf-news-radar` | находит, дедуплицирует и ранжирует темы, но не пишет посты |
| `gconf-news-writer` | пишет новости только по выбранным человеком topic ID |
| `gconf-announcement-analysis` | исследует аудиторию и предлагает направления анонса |
| `gconf-announcement-writer` | пишет анонс только по выбранному направлению и allowlist фактов |
| `gconf-instagram-carousel-designer` | превращает одобренные шесть слайдов в проверенные изображения |
| `gconf-telegram-formatter` | форматирует одобренный текст для ручной публикации |

У каждого skill есть собственный `SKILL.md`, reference contracts, валидаторы и, где необходимо, тесты. Полные правила маршрутизации, границы автоматизации, human gates и definition of done описаны в [`AGENTS.md`](AGENTS.md). AI-агенту перед работой нужно начать именно с этого файла.

## Быстрый старт

### Требования

Для чтения репозитория и сборки основной knowledge base достаточно:

- Git;
- Python 3 со стандартным модулем `sqlite3` и SQLite FTS5;
- любой современный браузер;
- опционально Obsidian для удобной навигации по `knowledge/`.

Отдельный `pip install` для основного индексатора не нужен. Для **нового сбора YouTube** дополнительно потребуются `yt-dlp`, `ffmpeg` и, только для fallback-транскрипции, `whisper.cpp` с моделью вне репозитория.

### 1. Клонировать и проверить окружение

```bash
git clone https://github.com/lunatik-210/gconf.git
cd gconf

python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py doctor
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py scan
```

`doctor` проверит Python, SQLite/FTS5 и наличие source directories. `scan` покажет доступные локальные пакеты, не изменяя их.

### 2. Проверить или обновить локальную базу

Готовый SQLite snapshot уже хранится в репозитории, поэтому после свежего clone можно сразу проверить его и выполнять поиск:

```bash
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py validate
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py search 'агенты OR контекст'
```

После добавления или обновления source packages пересоберите snapshot и провалидируйте его перед коммитом:

```bash
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py ingest --all
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py validate
```

Для поиска по timestamped-фрагментам YouTube-транскриптов используйте `search 'agent OR context' --chunks`.

`rebuild` нужен только для полного пересоздания производного индекса. Он не должен удалять source exports или проверенные semantic cards:

```bash
python3 -B .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py rebuild
```

### 3. Открыть knowledge base

Откройте папку `knowledge/` как vault в Obsidian и начните с [`knowledge/GCONF Knowledge.md`](knowledge/GCONF%20Knowledge.md). Без Obsidian карточки остаются обычными Markdown-файлами и доступны через любой редактор.

Проверить состояние semantic extraction можно так:

```bash
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py status --scope next-gconf
python3 -B .agents/skills/gconf-insight-extract/scripts/insight_extract.py validate
```

Завершённый processing batch означает, что evidence был обработан, но не означает автоматического одобрения найденных карточек.

### 4. Посмотреть итоговый сайт

Сайт полностью статический и не требует сборщика:

```bash
python3 -m http.server 8000 --directory submission-site
```

Откройте [http://localhost:8000](http://localhost:8000). Для деплоя достаточно отдать содержимое `submission-site/` любому static hosting; серверная часть и переменные окружения не нужны.

### 5. Начать работу через Codex / AI-агента

1. Откройте корень репозитория как workspace.
2. Дайте агенту прочитать [`AGENTS.md`](AGENTS.md).
3. Формулируйте задачу через нужный этап, например: «проиндексируй этот уже собранный пакет», «собери radar возможных новостей» или «напиши темы `topic-02` и `topic-05` из этого radar run».
4. Не просите перескочить через человеческий выбор: downstream skills потребуют зафиксированный `decision_id`.

Пример полного добавления YouTube-источника:

```text
$gconf-youtube-research <URL>
→ $gconf-knowledge-ingest <video_folder>
→ $gconf-insight-extract (если нужны новые semantic candidates)
```

Перед первым live-сбором YouTube запустите диагностику:

```bash
python3 -B .agents/skills/gconf-youtube-research/scripts/youtube_collect.py doctor
```

Инсталляторы, модели, cookies и credentials не запускаются и не сохраняются автоматически.

## Проверки и безопасная работа с данными

- Не редактируйте raw exports ради исправления результата анализа.
- Не добавляйте в репозиторий cookies, browser profiles, `.env`, ключи или Whisper-модели.
- Не считайте live web observation проиндексированным evidence: сначала нужен валидный локальный source package.
- Не используйте `knowledge/_index/gconf.sqlite` как долговременное хранилище ручных заметок — индекс пересобирается.
- Перед публичным текстом прочитайте [`editorial/gconf-tone-of-voice.md`](editorial/gconf-tone-of-voice.md) и выберите один voice mode и форму обращения.
- После добавления источников выполняйте `scan`, `ingest` и `validate`; после semantic extraction — отдельный human review.
- Даты, цены, программа, кейсы, цитаты, CTA и права на публикацию всегда требуют явного подтверждения.

## Где читать дальше

- [`AGENTS.md`](AGENTS.md) — полная операционная архитектура и правила для агентов;
- [`editorial/gconf-tone-of-voice.md`](editorial/gconf-tone-of-voice.md) — канонический голос публичного контента;
- [`knowledge/GCONF Knowledge.md`](knowledge/GCONF%20Knowledge.md) — главная страница Obsidian vault;
- [`YouTube/README.md`](YouTube/README.md) — сбор и нормализация YouTube;
- [`Web Articles/README.md`](Web%20Articles/README.md) — контракт локальных снимков статей;
- [`.agents/skills/`](.agents/skills/) — инструкции, контракты, CLI и тесты каждого этапа.

---

Главный принцип проекта: **автоматизировать повторяемую работу, но оставлять вкус, ответственность и право публикации человеку**.
