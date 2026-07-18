# GCONF News Radar

## Вердикт по данным и свежести

Новый run сфокусирован только на форматах `flash`, `gconf_field_note` и `story_lore`. В backlog вошли шесть проходящих тем: по две на каждый запрошенный формат. Пять имеют статус `recommended`, одна — `reserve`.

Live-окно: 4–18 июля 2026 года. Расширение до 45 дней применено только к двум развивающимся последовательностям: shutdown GitHub Models получил новый brownout 16 июля, а июньская история Fable 5 — новый институциональный шаг GOLD EAGLE 14 июля.

Локальная проверка использовала 321 документ полного публичного архива AI LOVERS, 29 semantic cards в compact context, предыдущий radar-run и отдельный coverage query для каждой shortlisted темы. Внешние источники GitHub, Anthropic и White House пока не индексированы и поэтому отмечены как `unindexed_observation` и помещены в ingestion queue.

## Приоритетный backlog

### 1. `news-20260706-claude-code-origin-story` — Как внутренний CLI Anthropic стал Claude Code

- **Статус / балл:** `recommended`, **89/100**.
- **Событие и дата:** 6 июля Anthropic опубликовала oral history о пути Claude Code от внутреннего CLI до публичного coding agent.
- **Один фокус:** собственная повторяемая боль команды → внутреннее использование → слабые ранние сигналы → устойчивая привычка → продукт.
- **Почему сейчас:** материал вышел 12 дней назад и впервые добавляет происхождение продукта, а не ещё один список функций.
- **Значение для AI-рынка:** показывает, как agentic-продукт может кристаллизоваться из внутреннего workflow, а не только из roadmap.
- **Связь со следующим GCONF:** среда, практика, agent-first процесс и способность заметить продукт внутри собственной операционки.
- **Для кого:** создатели продуктов, небольшие команды, vibe coders и пользователи Claude Code.
- **Было → стало:** отдельный продукт сначала проектируют, потом внедряют → команда сначала решает собственную боль, затем продукт вырастает из практики.
- **Ближайшее покрытие:** `telegram:1633415027:906`, `telegram:1633415027:907`.
- **Coverage delta:** AI LOVERS объяснял рабочий сетап и model releases, но не рассказывал происхождение Claude Code и последовательность внутренних решений.
- **Формат:** `story_lore`.
- **Эксперимент / вопрос:** проверить один внутренний tool: какую регулярную боль он снимает, кто возвращается к нему сам и какой usage artifact это подтверждает.
- **Факты:** официальная история опубликована 6 июля; источник описывает переход от internal CLI к публичному продукту через свидетельства команды и ранних пользователей.
- **Inference:** частота внутреннего использования может быть сильнее первоначальной внешней реакции как ранний product signal.
- **Ограничения:** ретроспектива подготовлена самой Anthropic и подвержена survivorship bias.
- **Редакционные риски:** не превращать историю в миф о неизбежном успехе и не добавлять непроверенные growth-метрики.
- **Evidence:** `ev-anthropic-making-claude-code`.
- **Почему приоритет №1:** наиболее чистое соответствие Story Lore, высокая новизна для GCONF и понятный практический вывод без product-hype.

### 2. `news-20260714-fable-cyber-governance-sequence` — Как один jailbreak превратился в новый контур управления frontier-моделями

- **Статус / балл:** `recommended`, **85/100**.
- **Событие и дата:** цепочка 9 июня–14 июля: launch Fable 5, suspension, redeploy, jailbreak severity framework и запуск GOLD EAGLE.
- **Один фокус:** переход от отдельного access-инцидента к совместной инфраструктуре testing, severity scoring, disclosure и vulnerability coordination.
- **Почему сейчас:** GOLD EAGLE 14 июля дал live-продолжение истории, начавшейся за пределами 14-дневного окна.
- **Значение для AI-рынка:** доступность frontier-модели зависит уже не только от capability и цены, но и от governance release-layer.
- **Связь со следующим GCONF:** чем больше полномочий получает агент, тем важнее заранее определить проверку, остановку и возврат процесса.
- **Для кого:** продвинутые пользователи, founders и AI-продуктовые команды.
- **Было → стало:** safeguards как внутренняя функция поставщика → межорганизационный контур pre-release testing, severity framework и координации.
- **Ближайшее покрытие:** `telegram:1633415027:1030`, `telegram:1633415027:904`.
- **Coverage delta:** AI LOVERS сообщал об условиях возврата Fable 5, но не собирал полную governance-последовательность и GOLD EAGLE.
- **Формат:** `story_lore`.
- **Эксперимент / вопрос:** выписать для одного agentic workflow собственную шкалу: harmless failure, manual confirmation, stop condition и decision owner для возврата.
- **Факты:** Anthropic запустила модели 9 июня, приостановила доступ 12 июня, объявила redeploy 30 июня, опубликовала framework 2 июля; White House объявил GOLD EAGLE 14 июля.
- **Inference:** frontier-model governance становится операционной частью релизного процесса.
- **Ограничения:** исходный Amazon jailbreak report не найден публично; эффективность GOLD EAGLE пока не доказана; причинная связь не установлена.
- **Редакционные риски:** не выдавать позицию Anthropic за нейтральный консенсус и не утверждать, что Fable-инцидент единолично вызвал GOLD EAGLE.
- **Evidence:** `ev-anthropic-fable-launch`, `ev-anthropic-fable-suspension`, `ev-anthropic-fable-redeploy`, `ev-anthropic-fable-framework`, `ev-whitehouse-ai-cyber-eo`, `ev-whitehouse-gold-eagle`.
- **Почему приоритет №2:** сильная документированная история с двумя независимыми официальными издателями и свежим институциональным финалом.

### 3. `news-20260714-github-ai-security-detections` — AI security detections появились прямо в pull request

- **Статус / балл:** `recommended`, **84/100**.
- **Событие и дата:** 14 июля GitHub запустила public preview AI-powered security detections в code scanning.
- **Один фокус:** finding входит в обычный PR review-loop до merge, но остаётся informational и требует человеческого решения.
- **Почему сейчас:** функция вышла четыре дня назад и меняет конкретный шаг agentic coding workflow.
- **Значение для AI-рынка:** AI входит не только в generation, но и в validation layer; происхождение finding помечается отдельно.
- **Связь со следующим GCONF:** проверка результата, human-in-the-loop и governance вокруг доступа агента.
- **Для кого:** vibe coders, технические founders и команды, принимающие pull requests от coding agents.
- **Было → стало:** AI пишет код, security review живёт отдельно → AI finding появляется внутри PR alongside CodeQL до merge.
- **Ближайшее покрытие:** `telegram:1633415027:904`, `telegram:1633415027:1058`.
- **Coverage delta:** GCONF не покрывал AI security findings внутри PR, их маркировку, условия включения и неблокирующий статус.
- **Формат:** `flash`.
- **Эксперимент / вопрос:** на некритичном repo сравнить review с AI detections и без них по новым классам проблем, false positives и подтверждённым findings.
- **Факты:** public preview требует GitHub Code Security, CodeQL default setup, Copilot license и AI credits; finding помечается `AI` и не блокирует merge.
- **Inference:** review-layer становится самостоятельной частью стоимости agentic coding.
- **Ограничения:** enterprise-centric release; нет независимой оценки точности или false-positive rate.
- **Редакционные риски:** не называть функцию гарантией безопасности и не скрывать billing-условия.
- **Evidence:** `ev-github-ai-security`.
- **Почему приоритет №3:** самый чистый Flash: один свежий delta, прямой источник, чёткое ограничение и маленький experiment.

### 4. `news-20260716-github-models-retirement-brownout` — GitHub Models вошёл в финальную фазу отключения

- **Статус / балл:** `recommended`, **84/100**.
- **Событие и дата:** первый brownout прошёл 16 июля; второй назначен на 23 июля; полный shutdown — 30 июля.
- **Один фокус:** migration deadline для playground, model catalog, inference API и BYOK endpoints.
- **Почему сейчас:** первая проверка отказа уже произошла внутри live-окна, до следующей остаётся меньше недели.
- **Значение для AI-рынка:** даже официальный model-access layer может быстро исчезнуть; portability и fallback проверяются до сбоя.
- **Связь со следующим GCONF:** владение процессом, минимальный стек, обратимость и замена инфраструктурного слоя.
- **Для кого:** разработчики и небольшие команды, использующие GitHub Models.
- **Было → стало:** стабильная точка доступа к model catalog → обязательный migration plan до 30 июля.
- **Ближайшее покрытие:** `telegram:1633415027:929`, `telegram:1633415027:1029`.
- **Coverage delta:** GCONF писал о routing и выборе стека, но не о retirement GitHub Models и scheduled brownouts.
- **Формат:** `flash`.
- **Эксперимент / вопрос:** до 23 июля найти все вызовы GitHub Models, назначить fallback и проверить один запрос через замену provider.
- **Факты:** shutdown касается всех пользователей; scope включает playground, catalog, inference API, BYOK и UI; brownouts — 16 и 23 июля.
- **Inference:** scheduled brownout полезно использовать как recovery drill.
- **Ограничения:** исходный анонс вышел 1 июля; live-основание — brownout 16 июля; тема узка для не-пользователей GitHub Models.
- **Редакционные риски:** не смешивать GitHub Models с GitHub Copilot и не рекомендовать migration target без workload-check.
- **Evidence:** `ev-github-models-retirement`.
- **Почему приоритет №4:** узкая, но срочная и полностью проверяемая Flash-тема с deadline и прямым действием.

### 5. `news-20260713-gconf-telegram-control-plane` — От одного поста через Codex к Telegram как control plane команды

- **Статус / балл:** `recommended`, **81/100**.
- **Событие и дата:** 6 июня Codex отправил пост и вложение; 1 июля появился персональный Telegram ops-loop; 13 июля команда описала Telegram как центр коммуникации и управления.
- **Один фокус:** изменение интерфейса работы: Telegram — вход, агент держит контекст, человек задаёт права и требования.
- **Почему сейчас:** свежая точка опубликована пять дней назад и завершает наблюдаемую пятинедельную последовательность.
- **Значение для AI-рынка:** consumer messenger становится control plane, но вместе с удобством растёт риск доступа к чатам и действиям.
- **Связь со следующим GCONF:** собственная практика AI Ops, context, минимальные права и agent-first интерфейс.
- **Для кого:** участники GCONF, небольшие команды и founders без желания строить отдельный dashboard.
- **Было → стало:** Telegram — только канал общения → Telegram — точка постановки задачи и наблюдения за agentic-процессом.
- **Ближайшее покрытие:** `telegram:1633415027:1006`, `telegram:1633415027:1029`, `telegram:1633415027:1058`.
- **Coverage delta:** стадии опубликованы отдельно; новая единица — хронология интерфейса и decision rights. Без нового end-to-end walkthrough тема становится duplicate.
- **Формат:** `gconf_field_note`.
- **Эксперимент / вопрос:** показать один актуальный workflow: Telegram input, context, действие агента, manual gate, результат и permission boundary.
- **Факты:** все три стадии подтверждены публичными first-party постами GCONF.
- **Inference:** messenger становится control plane, когда связывает задачу, контекст, разрешения и наблюдение.
- **Ограничения:** нет technical architecture, error log, cost и полного permission model; «полностью перевезли процессы» — self-report.
- **Редакционные риски:** не раскрывать credentials и внутренние чаты, не изображать широкий доступ безопасным default, не универсализировать отказ от UI.
- **Evidence:** `ev-gconf-codex-telegram`, `ev-gconf-openclaw-ops`, `ev-gconf-team-processes`.
- **Почему приоритет №5:** сильнейший собственный Field Note, но публикация оправдана только при появлении нового workflow-артефакта.

## Резерв

### `news-20260708-gconf-format-time-horizon` — Что успевает измениться за два дня и за три недели практики GCONF

- **Статус / балл:** `reserve`, **74/100**.
- **Событие и дата:** 8 июля GCONF подвёл итоги первого AI weekend; более ранние public case roundups описывают результаты трёхнедельного потока.
- **Один фокус:** сравнить тип первого действия и глубину артефакта при разных timeboxes, не объявляя один формат лучше другого.
- **Почему сейчас:** первый weekend завершился десять дней назад и добавил новый формат к документированным трёхнедельным циклам.
- **Значение для AI-рынка:** adoption зависит не только от model capability, но и от дизайна среды, timebox, совместной работы и своей задачи.
- **Связь со следующим GCONF:** помогает разделить activation-format и длинный цикл практики.
- **Для кого:** новички между ChatGPT и первым агентом, а также команда GCONF, проектирующая форматы входа.
- **Было → стало:** один формат должен снять барьер и довести систему → короткий timebox оценивается по первому loop, длинный — по повторяемости и поддержке.
- **Ближайшее покрытие:** `telegram:1633415027:1001`, `telegram:1633415027:1028`, `telegram:1633415027:1046`.
- **Coverage delta:** кейсы уже опубликованы; новый слой — сравнение механизмов поведения. Он остаётся inference до follow-up.
- **Формат:** `gconf_field_note`.
- **Эксперимент / вопрос:** одинаковый follow-up участникам: запускался ли артефакт второй раз, что осталось ручным, где сломался и какая поддержка потребовалась.
- **Факты:** weekend дал билетный монитор, Telegram-календарь и прототип игры; длинный поток публиковал более сложные рабочие системы.
- **Inference:** два дня могут снять стартовый барьер, но не доказывают устойчивость; различия нельзя приписать только длительности.
- **Ограничения:** выборки несопоставимы, промо-отобраны и основаны преимущественно на organizer/self-report без follow-up.
- **Редакционные риски:** не утверждать causality, не обещать аналогичный результат каждому, не расширять анонимные цитаты без permission-check.
- **Evidence:** `ev-gconf-three-week-cases`, `ev-gconf-case-roundup`, `ev-gconf-weekend-results`, `ev-card-ticket-monitor`, `ev-card-telegram-calendar`.
- **Почему резерв:** полезный field hypothesis, но evidence selection bias и отсутствие повторного замера пока не позволяют делать сильный вывод.

## Отклонённые сильные сигналы

Дополнительных сильных сигналов, которые стоило бы сохранять как обучающие reject, в этом форматном проходе нет. Прежние `release_explainer` и `trend_translation` не переупаковывались в новые рубрики только ради квоты.

## Покрытие GCONF и дубли

- Claude Code origin проходит: прежние посты покрывали инструмент, сетап и релизы, но не documented origin sequence.
- Fable governance проходит: access update `1030` не содержит jailbreak framework, cross-organization testing или GOLD EAGLE.
- GitHub AI security detections проходит: прямого entity и PR-review delta в архиве нет.
- GitHub Models retirement проходит: routing обсуждался, provider shutdown и brownouts — нет.
- Telegram control plane проходит условно: источники уже опубликованы, поэтому новый материал нужен только как новая хронология с fresh walkthrough. Без него кандидат должен быть отклонён как duplicate.
- Format time horizon остаётся reserve: case outcomes опубликованы, а сравнительный вывод пока является проверяемой гипотезой, а не фактом.

## Пробелы и ingestion queue

Для воспроизводимости нужно отдельно сохранить в локальный pipeline:

1. Anthropic — `The Making of Claude Code`.
2. Anthropic — полный пакет Fable 5: launch, suspension, redeploy, jailbreak framework.
3. White House — EO 14409 и GOLD EAGLE.
4. GitHub — AI security detections in PRs.
5. GitHub — GitHub Models retirement and brownouts.

Для двух Field Note перед публикацией не хватает новых evidence artifacts: end-to-end walkthrough Telegram workflow и одинакового follow-up участников weekend/трёхнедельного формата. Radar не запускал ingestion и не менял SQLite, Obsidian или source exports.

## Human review

Проверьте сначала границы двух Field Note:

- `news-20260713-gconf-telegram-control-plane` выбирать только если команда готова дать новый безопасный workflow-артефакт.
- `news-20260708-gconf-format-time-horizon` выбирать только после follow-up или с явной маркировкой как hypothesis.

Ни одна тема не выбрана автоматически: `selected_topic_ids: []`.

Для следующего шага передайте точный run и выбранные IDs в `$gconf-news-writer`. Например: `$gconf-news-writer Возьми radar-run research/news_analysis/runs/20260718T155013Z и тему <TOPIC_ID>.`

## Evidence appendix

- Anthropic, 6 июля: <https://www.anthropic.com/features/making-of-claude-code>
- Anthropic, Fable sequence: <https://www.anthropic.com/news/claude-fable-5-mythos-5>, <https://www.anthropic.com/news/fable-mythos-access>, <https://www.anthropic.com/news/redeploying-fable-5>, <https://www.anthropic.com/news/fable-safeguards-jailbreak-framework>
- White House, EO 14409 и GOLD EAGLE: <https://www.whitehouse.gov/presidential-actions/2026/06/promoting-advanced-artificial-intelligence-innovation-and-security/>, <https://www.whitehouse.gov/releases/2026/07/white-house-launches-gold-eagle-initiative-for-unprecedented-cybersecurity-vulnerability-coordination/>
- GitHub AI security detections: <https://github.blog/changelog/2026-07-14-code-scanning-shows-ai-security-detections-on-pull-requests/>
- GitHub Models retirement: <https://github.blog/changelog/2026-07-01-github-models-is-being-fully-retired-on-july-30-2026/>
- GCONF field evidence: `telegram:1633415027:1001`, `1006`, `1028`, `1029`, `1046`, `1058`.
- Approved local cards: `knowledge:case-ai-weekend-ticket-slot-monitor`, `knowledge:case-ai-weekend-telegram-calendar`.

Полный evidence index, freshness, limitations и score arithmetic находятся в `manifest.json` и `audit.md`.
