# GCONF News Radar

Run: `20260718T145438Z`  
Срез: 18 июля 2026 года  
Режим: исследовательский backlog, без публичных текстов и без выбора тем за редактора.

## Вердикт по данным и свежести

Radar нашёл пять тем со статусом `recommended` и одну тему в `reserve`. Квота не заполнялась искусственно. Основной поиск ограничен 14 днями; до 45 дней расширен только структурный сигнал про научных агентов, где релиз Claude Science от 30 июня получил независимое продолжение в июльском материале Google DeepMind.

Сильнейший общий сдвиг окна: рынок начинает продуктировать не просто автономность, а инфраструктуру вокруг неё — reviewer-роли, происхождение результата, управление контекстом, параллельными сессиями и стоимостью. Для GCONF это полезнее очередного списка моделей: тема непосредственно поддерживает переход от разового демо к наблюдаемому и ремонтопригодному процессу.

Live web-источники Meta, Anthropic, DeepMind и GitHub пока отсутствуют в локальном ingestion. Они использованы как `unindexed_observation` и поставлены в очередь, но автоматический ingestion не запускался.

## Приоритетный backlog

### 1. `news-20260630-science-validation-bottleneck` — Научные агенты ускоряют гипотезы, а узким местом становится проверка

- **Статус / балл:** `recommended`, **95/100**.
- **Событие и дата:** 30 июня Anthropic открыла beta Claude Science с воспроизводимыми артефактами и reviewer-agent; в июле Google DeepMind отдельно назвала валидацию AI-сгенерированных идей новым bottleneck науки.
- **Один фокус:** ценность агентной системы растёт вместе с provenance, воспроизводимостью, reviewer-ролью и человеческой точкой решения.
- **Почему сейчас:** два независимых разработчика в одном временном окне сместили разговор с генерации идей на проверяемость результатов.
- **Значение для AI-рынка:** вокруг исполнителя формируется отдельный validation layer — след результата, критик, повторяемость и governance.
- **Связь со следующим GCONF:** прямая опора для цикла `задача → контекст → действие → проверка → улучшение`.
- **Для кого:** исследователи, аналитики и команды, делегирующие агентам задачи с высокой ценой ошибки.
- **Было → стало:** скорость получения артефакта → проектирование артефакта вместе с проверкой и воспроизводимым следом.
- **Ближайшее покрытие:** `telegram:1633415027:971`, `telegram:1633415027:1058`.
- **Coverage delta:** канал уже объяснял capability shift и agent-first архитектуру, но не разбирал validation layer как отдельную часть рынка и workflow.
- **Формат:** `trend_translation`.
- **Маленький эксперимент:** отметить в одном текущем workflow источник, способ воспроизведения, reviewer и точку человеческого решения.
- **Факты:** Claude Science заявляет auditable history и reviewer-agent; DeepMind фиксирует системную проблему проверки потока новых AI-гипотез.
- **Inference:** паттерн reviewer/provenance/reproducibility будет переноситься из science в другие высокорисковые процессы.
- **Ограничения:** оба источника корпоративные; Claude Science — beta; у материала DeepMind нет точного дня публикации.
- **Редакционные риски:** не обещать автономные научные открытия и не подменять наличие reviewer-agent доказанной безопасностью.
- **Evidence:** `ev-deepmind-validation`, `ev-anthropic-science`, `ev-local-output-validation`.
- **Почему приоритет №1:** максимальная связь с AI Ops, два независимых первичных сигнала и применимое действие без необходимости продавать конкретный продукт.

### 2. `news-20260708-benchmark-method-audit` — Лидерборд без аудита методологии перестаёт быть решением

- **Статус / балл:** `recommended`, **89/100**.
- **Событие и дата:** 8 июля OpenAI сообщила, что около 30% задач SWE-Bench Pro имеют breaking issues, и отозвала прежнюю рекомендацию использовать benchmark.
- **Один фокус:** модель нужно выбирать после проверки методологии и одинакового прикладного теста, а не по месту в launch-таблице.
- **Почему сейчас:** релизные benchmark появляются еженедельно, а свежий аудит затронул широко используемый eval agentic coding.
- **Значение для AI-рынка:** слабый eval искажает product, infrastructure и safety decisions; агенты одновременно становятся инструментом аудита evals.
- **Связь со следующим GCONF:** практический мост между выбором модели, стоимостью workflow и проверкой результата.
- **Для кого:** пользователи и команды, выбирающие подписки и API по benchmark-таблицам.
- **Было → стало:** один aggregate score → одинаковая задача, одинаковый harness и бюджет, плюс число повторов, latency и человеческая проверка.
- **Ближайшее покрытие:** `telegram:1633415027:907`, `telegram:1633415027:929`.
- **Coverage delta:** GCONF публиковал benchmark-цифры и model routing, но ещё не разбирал, почему методология должна проверяться до выбора.
- **Формат:** `trend_translation`.
- **Маленький эксперимент:** сравнить две модели на одной задаче с общим критерием готовности и полной стоимостью проверки.
- **Факты:** OpenAI указывает 27,4% проблемных задач по pipeline и 34,1% по human annotation; прежняя рекомендация отозвана.
- **Inference:** методологический аудит становится прикладным навыком владельца AI-workflow.
- **Ограничения:** вывод относится к одному coding benchmark; источник — участник модельного рынка.
- **Редакционные риски:** не писать, что все benchmark бессмысленны, и не строить новый рейтинг на тех же сомнительных основаниях.
- **Evidence:** `ev-openai-benchmark`, `ev-local-benchmark-card`.
- **Почему приоритет №2:** высокий coverage delta и понятный эксперимент для аудитории; ниже №1 из-за одного корпоративного первичного источника.

### 3. `news-20260717-kimi-k3-open-frontier` — Kimi K3 расширяет выбор открытых моделей для длинных agentic-задач

- **Статус / балл:** `recommended`, **86/100**.
- **Событие и дата:** 17 июля Kimi представила K3; модель доступна в собственных продуктах и API, а полные веса и technical report обещаны позже.
- **Один фокус:** важен не publisher benchmark, а расширение практического выбора между закрытыми и открытыми стеками для long-horizon work.
- **Почему сейчас:** самый свежий релиз окна продолжает июньский сигнал GLM-5.2 и добавляет новый вариант для routing.
- **Значение для AI-рынка:** выбор всё чаще зависит от качества, цены, доступа, harness compatibility и контроля инфраструктуры, а не от одной «лучшей» модели.
- **Связь со следующим GCONF:** минимальный рабочий стек, стоимость и выбор достаточной модели под реальный процесс.
- **Для кого:** продвинутые пользователи, vibe coders и небольшие команды с API-расходами и длинными задачами.
- **Было → стало:** одна frontier-подписка → routing между hosted-продуктом, API и будущим self-hosting после проверки совместимости.
- **Ближайшее покрытие:** `telegram:1633415027:929`, `telegram:1633415027:907`.
- **Coverage delta:** Kimi K3 и свежая волна китайских open frontier моделей в канале не покрыты.
- **Формат:** `release_explainer`.
- **Маленький эксперимент:** после повторной проверки доступности сравнить K3 с текущей моделью на длинной задаче по качеству, повторам, latency, цене и сбоям контекста.
- **Факты:** издатель заявляет 2,8T параметров, native vision, контекст до 1M и текущий доступ через Kimi/Work/Code/API.
- **Inference:** открытые модели становятся вариантом реального routing, а не только исследовательским watchlist.
- **Ограничения:** benchmark и showcases publisher-only; веса ещё не выпущены; Kimi указывает harness sensitivity и excessive proactiveness.
- **Редакционные риски:** не называть модель лучшей или полностью открытой до выхода весов и независимой проверки.
- **Evidence:** `ev-kimi-k3`, `ev-local-open-frontier`, `ev-local-model-routing`.
- **Почему приоритет №3:** максимальная свежесть и отсутствие прежнего покрытия, но существенный hype/availability penalty.

### 4. `news-20260707-muse-image-agentic-media` — Генерация изображений становится агентным процессом с поиском и самопроверкой

- **Статус / балл:** `recommended`, **85/100**.
- **Событие и дата:** 7 июля Meta запустила Muse Image с search, coding tools и self-refinement; rollout ограничен продуктами и регионами.
- **Один фокус:** visual workflow переходит от одного prompt к циклу `данные → черновик → проверка → исправление`.
- **Почему сейчас:** agentic loop выходит из coding и текста в массовое визуальное производство.
- **Значение для AI-рынка:** media models начинают конкурировать инструментами, grounding и итеративным исправлением, а не только качеством пикселей.
- **Связь со следующим GCONF:** наглядный non-code пример живого процесса с контекстом, действием и проверкой.
- **Для кого:** контент-команды, маркетологи, дизайнеры и creators.
- **Было → стало:** prompt → image → новый ручной prompt → модель сама ищет, использует код, проверяет и локально исправляет.
- **Ближайшее покрытие:** `telegram:1633415027:971`, `telegram:1633415027:1050`.
- **Coverage delta:** tool-using media model и self-refinement как производственный loop ранее не освещались.
- **Формат:** `release_explainer`.
- **Маленький эксперимент:** дать фактозависимый визуальный бриф и отдельно проверить источники, текст, вычисления и provenance.
- **Факты:** Muse Image доступна в Meta AI/meta.ai, Instagram Stories в США и WhatsApp в ограниченных странах; Muse Video только preview.
- **Inference:** навык автора смещается от одного prompt к критериям качества и проверке trace.
- **Ограничения:** региональный rollout; корпоративные evals; поиск не гарантирует корректность результата.
- **Редакционные риски:** не выдавать self-refinement за надёжный fact-check и не смешивать Image с ещё недоступным Video.
- **Evidence:** `ev-meta-muse-image`.
- **Почему приоритет №4:** новый и понятный широкой аудитории процессный угол, но доступность пока неоднородна.

### 5. `news-20260709-muse-spark-orchestration` — Оркестрация параллельных субагентов становится свойством базовой модели

- **Статус / балл:** `recommended`, **84/100**.
- **Событие и дата:** 9 июля Meta открыла public preview Muse Spark 1.1 и заявила нативные main/subagent роли, parallel delegation и context compaction.
- **Один фокус:** модель для AI Ops оценивается по удержанию роли, делегированию, контексту и эскалации, а не только по ответу.
- **Почему сейчас:** multi-agent orchestration переходит из внешнего framework-паттерна в заявленную способность model runtime.
- **Значение для AI-рынка:** модели всё больше работают как runtime процессов с ролями, контекстом и управлением latency.
- **Связь со следующим GCONF:** архитектура агентного процесса и границы ответственности.
- **Для кого:** продвинутые пользователи и команды, которые уже делят работу на research, execution и review.
- **Было → стало:** внешний framework вручную распределяет роли → модель обучена действовать как main agent или дисциплинированный subagent.
- **Ближайшее покрытие:** `telegram:1633415027:931`, `telegram:1633415027:1058`.
- **Coverage delta:** канал упоминал subagents и agent-first процессы, но не релиз модели, специально обученной orchestration и compaction.
- **Формат:** `release_explainer`.
- **Маленький эксперимент:** сравнить последовательный процесс и три роли по времени, цене, согласованности контекста и числу эскалаций.
- **Факты:** public preview доступен через Meta Model API; Meta заявляет MCP, skills, parallel subagents и 1M context management.
- **Inference:** orchestration становится отдельным критерием выбора модели.
- **Ограничения:** preview, publisher-only evals, возможный рост стоимости и сложности контроля.
- **Редакционные риски:** не подавать multi-agent как универсально лучший способ работы.
- **Evidence:** `ev-meta-spark`.
- **Почему приоритет №5:** очень высокая связь с AI Ops, но тема техническая и требует особенно аккуратного перевода для широкой аудитории.

## Резерв

### `news-20260708-copilot-agent-control-plane` — В IDE появляется control plane для параллельных агентов и их стоимости

- **Статус / балл:** `reserve`, **77/100**.
- **Событие и дата:** 8 июля GitHub собрала обновления Copilot в VS Code: parallel sessions/chats, total session cost, subagent usage, model marketplace и agentic browser tools.
- **Один фокус:** интерфейс управления работой, историей и стоимостью нескольких агентов становится таким же важным, как модель.
- **Почему сейчас:** GitHub одновременно добавила параллельность и наблюдаемость расходов.
- **Значение для рынка:** agent products превращаются в control planes с сессиями, делегированием и usage.
- **Связь с GCONF:** наблюдаемость и стоимость lifecycle после первого агента.
- **Для кого:** vibe coders, разработчики и команды с несколькими coding agents.
- **Было → стало:** отдельные окна и непрозрачный расход → общая панель с session/subagent usage.
- **Ближайшее покрытие:** `telegram:1633415027:1029`, `telegram:1633415027:1058`.
- **Coverage delta:** cost observability и subagent usage в массовой IDE ещё не разбирались.
- **Формат:** `release_explainer`.
- **Эксперимент:** разделить implementation, review и docs на chats и проверить полезность session cost visibility.
- **Факты / inference:** функции подтверждены changelog; перенос идеи за пределы development пока inference.
- **Ограничения:** dev-centric; сводка объединяет несколько версий; visibility не равно cost optimization.
- **Редакционные риски:** не пересказывать feature list и не обещать автоматическое ускорение.
- **Evidence:** `ev-github-copilot`.
- **Почему резерв:** AI Ops угол сильный, но аудитория уже и пересечение с собственными field notes GCONF выше.

## Отклонённые сильные сигналы

- `news-20260709-chatgpt-work-convergence` — **79/100, reject**. Сильный релиз, но entity, центральный claim, behavioral transition и GCONF-угол уже опубликованы в `telegram:1633415027:1049` и связаны с потоком в `telegram:1633415027:1040`. Возвращаться только при новом rollout delta или собственном проверенном кейсе.
- `news-20260709-claude-reflection-dashboard` — **63/100, reject**. Anthropic добавила новый wellbeing-слой, но рекомендуемый фокус «AI как зеркало рабочих привычек» уже является центром `telegram:1633415027:931`. Пока нет доказанного нового behavioral consequence.

## Покрытие GCONF и дубли

- Архив проверен семантически: entity/release, центральный claim, behavioral transition, audience consequence и уже использованный GCONF-угол.
- Ключевой прямой дубль — ChatGPT Work: опубликован 10 июля, поэтому повторная новость отклонена несмотря на высокий внешний приоритет.
- Claude Reflection отклонён не по совпадению названия, а по совпадению смыслового угла с Claude Code `/insights`.
- Kimi K3 проходит: прежний пост про несколько моделей задаёт контекст, но не содержит эту сущность, open-stack consequence или текущие ограничения релиза.
- Benchmark audit проходит: прежний пост использовал benchmark-цифры, но не обсуждал качество самих evals.
- Science validation проходит: прежнее capability-покрытие не содержало provenance/reviewer/reproducibility как самостоятельный layer.
- Muse Image проходит: у канала нет прежнего tool-using visual agent и self-refinement loop.
- Muse Spark проходит с пониженной novelty: subagents уже упоминались, но model-native orchestration и active compaction — новый delta.
- Copilot остаётся резервом: новый delta есть, но field notes GCONF уже покрывают общий AI Ops тезис.

## Пробелы и ingestion queue

В локальном корпусе уже присутствуют Kimi K3 и OpenAI benchmark audit. Для последующей воспроизводимости стоит отдельно ingest официальные страницы:

1. Google DeepMind — validation bottleneck in science; нужно сохранить точную дату, если она появится в metadata.
2. Anthropic — Claude Science.
3. Meta — Muse Image / Muse Video.
4. Meta — Muse Spark 1.1.
5. GitHub — Copilot in VS Code June 2026 releases.
6. OpenAI — ChatGPT Work; нужен для аудита отклонённого дубля.
7. Anthropic — Reflection dashboard; нужен для аудита отклонённого дубля.

Radar не запускал ingestion и не изменял SQLite, Obsidian или исходные экспорты.

## Human review

Редактору нужно выбрать один или несколько `topic_id`, при необходимости уточнить угол и желаемое действие читателя. Исходный radar-run изменять не требуется.

После выбора передайте writer точный путь и ID, например:

`$gconf-news-writer Возьми radar-run research/news_analysis/runs/20260718T145438Z и тему news-20260630-science-validation-bottleneck. Подготовь Telegram-пост в режиме GCONF.`

Ни одна тема в этом run не выбрана автоматически: `selected_topic_ids: []`.

## Evidence appendix

- `ev-deepmind-validation` — Google DeepMind, July 2026: <https://deepmind.google/public-policy/conjecture-machines-ai-agents-and-the-new-validation-bottleneck-in-science/>
- `ev-anthropic-science` — Anthropic, 30 июня 2026: <https://www.anthropic.com/news/claude-science-ai-workbench>
- `ev-openai-benchmark` — OpenAI, 8 июля 2026: <https://openai.com/index/separating-signal-from-noise-coding-evaluations/>
- `ev-kimi-k3` — Kimi / Moonshot AI, 17 июля 2026: <https://www.kimi.com/blog/kimi-k3>
- `ev-meta-muse-image` — Meta, 7 июля 2026: <https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/>
- `ev-meta-spark` — Meta, 9 июля 2026: <https://ai.meta.com/blog/introducing-muse-spark-meta-model-api/>
- `ev-github-copilot` — GitHub, 8 июля 2026: <https://github.blog/changelog/2026-07-08-github-copilot-in-visual-studio-code-june-2026-releases/>
- Локальные semantic locators: `knowledge:pain-agent-output-validation`, `knowledge:claim-benchmark-leaderboards-require-method-audit`, `knowledge:trend-chinese-open-frontier-competition`, `knowledge:claim-model-selection-is-cost-quality-routing`.

Полный evidence index, freshness, locators, publisher-claim flags и ограничения находятся в `manifest.json`.
