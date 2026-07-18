# GCONF News Writer brief

Run: `20260718T154004Z`  
Radar run: `research/news_analysis/runs/20260718T145438Z`  
Human-selected topic: `news-20260717-kimi-k3-open-frontier`  
Source revalidation: `2026-07-18T15:40:04Z`

## Writing settings

- Режим: `GCONF`.
- Площадка: Telegram.
- Обращение: `вы`.
- CTA mode: `editorial`.
- Формат: `release_explainer`, 150–260 слов.
- Изменение формата относительно radar: нет.

## Topic contract

- **Выбранный фокус:** важен не заявленный benchmark rank, а расширение практического выбора моделей по задаче, стоимости, доступности, совместимости agent harness и границам поведения.
- **Аудитория:** продвинутые пользователи, vibe coders и небольшие команды, которые запускают длинные coding или knowledge-work задачи и оплачивают несколько моделей/API.
- **Поведенческий переход:** от поиска одной «лучшей модели» к одинаковому прикладному тесту и routing по реальной стоимости и качеству процесса.
- **Главное напряжение:** новый релиз легко добавить в коллекцию подписок, но publisher benchmark не отвечает, будет ли модель устойчивой в конкретном workflow.
- **Primary evidence:** `ev-kimi-k3`, Kimi / Moonshot AI, `web-live:kimi:kimi-k3:lines-27-38,104-139`.
- **Поддерживающее local evidence:** `ev-local-open-frontier`, `ev-local-model-routing`.
- **Материальное ограничение:** полные веса заявлены к 27 июля и ещё не опубликованы; technical report отсутствует; сравнения и showcase принадлежат Kimi.
- **GCONF theme:** минимальный рабочий стек, стоимость и осознанный выбор модели под процесс.
- **Coverage delta:** GCONF уже писал о нескольких моделях под разные задачи, но не покрывал Kimi K3 и не связывал новую open-model волну с harness compatibility и границами агентного поведения.
- **Один CTA:** сравнить K3 и текущую модель на одной длинной задаче по качеству, числу повторов, времени, цене и объёму ручной проверки.

## Live revalidation result

### Kimi / Moonshot AI

- URL доступен.
- Дата релиза: 17 июля 2026 года.
- Central fact: `unchanged`.
- Текущая доступность подтверждена официальной страницей: Kimi.com, Kimi app, Kimi Work 3.1.0+, Kimi Code и Kimi API.
- Заявленные характеристики: native vision, контекст до 1M токенов, long-horizon coding и knowledge work.
- Future promise: full model weights by 27 July 2026; technical report later. На момент revalidation это не считается выполненным.
- Publisher limitations: разные harness в benchmark; sensitivity to thinking history; риск excessive proactiveness; сам издатель отмечает UX gap относительно сильнейших proprietary alternatives.

### Z.ai / GLM-5.2 context

- Официальный URL доступен, но live parser не вернул содержимого.
- Для структурного контекста используется локальный checksum-backed snapshot через semantic cards; отдельные live claims GLM-5.2 в публичный пост не включаются.

## Fact / inference / proposal boundary

- **Fact:** K3 выпущена и доступна в hosted products/API; заявленные характеристики и ограничения опубликованы Kimi.
- **Inference:** растущий набор моделей делает routing по собственной задаче полезнее поиска одного leaderboard winner.
- **Proposal:** провести одинаковый прикладной тест и посчитать полную стоимость результата.

## Unresolved items

- Полные веса Kimi K3 ещё не опубликованы и не проверены.
- Technical report ещё не опубликован.
- Независимого прикладного теста K3 на workflow GCONF нет.

Эти пункты не меняют центральный факт релиза, но не позволяют маркировать draft как `publication_ready` без финального редакторского решения о формулировке «open».
