---
type: case
id: case-ai-weekend-ticket-slot-monitor
label: Агент два дня ловил билетные слоты для восьми человек
status: fact
review_status: approved
first_seen: 2026-07-08
last_seen: 2026-07-08
source_wave: internal
evidence:
  - telegram:1633415027:1046
evidence_quotes:
  - locator: telegram:1633415027:1046
    role: primary
    quote: Благодаря ему выловила слоты на билеты, которые не могла поймать вручную... 2 дня он работал, автоматически ловя слоты, и вот, билеты уже у меня в почте (и это на 8 человек!!!)
    supports: Организаторская цитата участницы о конкретном работающем результате AI weekend
related:
  - cohort-ai-weekend-july-2026
event_context:
  - event_id: cohort-ai-weekend-july-2026
    phase: after
    attribution: explicit
case_origin: gconf_participant
reporting_mode: organizer_report
proof_level: described_result
artifact_status: working
initial_task: Поймать редкие билетные слоты для восьми человек
process: Агент автоматически проверял доступность два дня
tools:
  - AI agent
result: Билеты оказались в почте участницы
behavior_shift: От ручного мониторинга к автономному процессу
limitations: Анонимная организаторская цитата; реализация не показана
---

# Агент два дня ловил билетные слоты для восьми человек

Свежий participant case с конкретным действием, длительностью и результатом.

<!-- evidence:start -->
## Evidence

### 1. GCONF / AI LOVERS · Telegram · 2026-07-08

- **Автор:** GCONF / AI LOVERS
- **Роль:** `primary`
- **Подтверждает:** Организаторская цитата участницы о конкретном работающем результате AI weekend
- **Visibility:** `public`

> Благодаря ему выловила слоты на билеты, которые не могла поймать вручную... 2 дня он работал, автоматически ловя слоты, и вот, билеты уже у меня в почте (и это на 8 человек!!!)

- Locator: `telegram:1633415027:1046`
- [Открыть источник](https://t.me/gptlovers/1046)
- Local source: `telegram/GCONF : AI LOVERS - All Time.json`

<!-- evidence:end -->
