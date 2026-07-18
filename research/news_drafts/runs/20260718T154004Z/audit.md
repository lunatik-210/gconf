# Audit — GCONF News Writer `20260718T154004Z`

## Boundary and selection

- Radar run: `research/news_analysis/runs/20260718T145438Z`.
- Explicit human selection: `news-20260717-kimi-k3-open-frontier`.
- Topic status in radar: `recommended`, 86/100.
- User wording `Chemical 3` interpreted as Kimi K3, the third ranked idea in the referenced backlog.
- Human selection boundary preserved: no topic discovery, substitution or focus change.
- Created exactly one Telegram post.
- No publication, ingestion, SQLite, Obsidian, source-export or prior-run mutation performed.

## Live source checks

Revalidated at `2026-07-18T15:40:04Z`.

### Kimi / Moonshot AI

- URL: <https://www.kimi.com/blog/kimi-k3>
- Available: yes.
- Published: 17 July 2026.
- Central fact: `unchanged`.
- Hosted availability confirmed by the official page: Kimi.com/app, Kimi Work 3.1.0+, Kimi Code and Kimi API.
- Future availability: full weights are still promised for 27 July; technical report remains future.
- Publisher claims: parameter count, context, capability comparisons, benchmarks, showcases and API cache performance.
- Publisher-disclosed limitations retained: dependence on preserved thinking history and compatible harness, unexpected decisions under ambiguity, UX gap versus named proprietary alternatives.

### Z.ai context

- URL: <https://z.ai/blog/glm-5.2>
- URL resolved, but live parser returned no content.
- No standalone GLM-5.2 fact was added to the public post.
- The local checksum-backed semantic card is used only for the broader inference that model choice is widening.

## Claim-to-evidence audit

| Material public claim | Status | Evidence |
|---|---|---|
| Kimi K3 was released on 17 July | fact | `ev-kimi-k3` |
| K3 has native vision, up to 1M context and 2.8T parameters | publisher fact | `ev-kimi-k3` |
| K3 is currently available in Kimi products and API | fact, live-revalidated | `ev-kimi-k3` |
| Full weights are not yet released and are promised for 27 July | current fact plus attributed future promise | `ev-kimi-k3` |
| Benchmark comparisons use different agent harnesses | fact from publisher methodology | `ev-kimi-k3` |
| K3 may become unstable without preserved thinking history or after a mid-session switch | publisher-disclosed limitation | `ev-kimi-k3` |
| Model routing is more useful than one universal winner | inference | `ev-local-model-routing`, `ev-local-open-frontier` |
| Five-part comparison is a useful next step | editorial proposal | brief CTA |

Result: material claims resolve to evidence; publisher claims are qualified; future weights are not presented as released.

## Coverage audit

- Closest prior posts: `telegram:1633415027:929`, `telegram:1633415027:907`.
- Central overlap: `partial` — model routing and model-release explanation are familiar formats.
- New editorial unit: yes.
- Delta: Kimi K3 is a new entity; the draft distinguishes hosted access from future open weights and translates the release through harness compatibility and agent boundaries rather than another leaderboard.

## Format and length audit

- Format: `release_explainer`.
- Radar format preserved.
- Word count: 249 by validator-compatible counting, within 150–260.
- Character count: 1,699 including Markdown source URL; consistent with the channel's long-form news range.
- Movement present: release → current access → real choice shift → limitations → one experiment.
- CTA count: 1 editorial CTA.
- Source link is attribution, not a second CTA.
- Emoji count: 0.
- Address: `вы`, consistent.

## Canonical voice audit

### Смысл

- [x] Да — один переход: universal winner → routing and workflow test.
- [x] Да — K3 поддерживает процессный смысл, а не заменяет его списком benchmark.
- [x] Да — живое напряжение: новая подписка не гарантирует устойчивость на собственной задаче.
- [x] Да — официальный release source и локальные source-backed inference cards.
- [x] Да — практика и человеческая проверка встроены в предложенный эксперимент.
- [x] Да — читателю возвращён выбор и установка границ; модель не изображена спасателем.

### Голос

- [x] Да — режим `GCONF`.
- [x] Да — обращение `вы`.
- [x] Да — короткие абзацы, живая, но вычитанная речь.
- [x] Да — нет инфопродуктовых штампов, FOMO и искусственной срочности.
- [x] Да — `hosted`, `routing`, `harness`, `workflow` используются функционально и раскрываются контекстом.
- [x] N/A — режим Димы не используется.

### Доказательность

- [x] Да — дата, доступность, характеристики и ограничения привязаны к official primary source.
- [x] Да — publisher fact, inference и proposal разведены.
- [x] N/A — кейсы и цитаты участников не используются.
- [x] Да — веса, technical report, benchmark methodology и behavioral limits не спрятаны.
- [x] Да — неизвестные cohort details не используются.

### Действие и рост

- [x] Да — один CTA.
- [x] Да — действие продолжает тезис о routing и полной стоимости результата.
- [x] Да — целевой сигнал: сохранения, содержательные ответы с результатами сравнения, доверие к редакционной осторожности.
- [x] N/A — пост не продажный.

## Unknown GCONF facts

Не использованы дата, цена, программа, speakers, capacity, результаты участников или коммерческие условия следующего GCONF.

## Quality rubric

| Критерий | Балл | Основание |
|---|---:|---|
| Taste | 2 | Релиз переведён в выбор поведения без гигантомании и leaderboard hype. |
| Philosophy | 2 | Видны система, границы, проверка и agency пользователя. |
| Research | 2 | Primary source revalidated; future promises and publisher claims qualified. |
| Process quality | 2 | Один сравнимый test и пять критериев результата. |
| Growth | 1 | CTA ведёт к полезному эксперименту, но tracking остаётся редакционным. |
| **Итого** | **9/10** | Threshold 8/10 выполнен, Research > 0. |

## Publication readiness

- Central fact: unchanged.
- Hosted availability: confirmed.
- Open weights: pending, not verified.
- Technical report: pending.
- Independent workflow evaluation: unavailable.
- Post status: `publication_ready: false`.
- Run status: `ready_for_human_review`.
- Reason: формулировка «open» требует редакторского принятия оговорки до выхода весов; автоматическая публикация запрещена.
