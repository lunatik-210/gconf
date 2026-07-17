---
type: case
id: case-gconf12-telegram-coach-memory
label: Telegram-коуч с памятью в Markdown
status: fact
review_status: approved
first_seen: 2026-05-23
last_seen: 2026-05-23
source_wave: internal
evidence:
  - telegram:1633415027:1001
evidence_quotes:
  - locator: telegram:1633415027:1001
    role: primary
    quote: |-
      я сделала коуч-бота на основе диминого промта, но немножко его под себя сделала.

      он у меня сидит в telegram, то есть мне теперь не нужен chat gpt или claude. я просто через telegram общаюсь с этим коучем. он точно так же помнит контекст, если не лучше.

      после каждого разговора он делает короткий md-файл саммари автоматом
    supports: Организаторский шеринг персонализированного коуч-бота участницы
related:
  - cohort-gconf-12-vibe-coding-mar-2026
  - technology-telegram-agent-interface
  - technology-obsidian-markdown-memory
event_context:
  - event_id: cohort-gconf-12-vibe-coding-mar-2026
    phase: after
    attribution: explicit
case_origin: gconf_participant
reporting_mode: organizer_report
proof_level: described_result
artifact_status: working
initial_task: Персонализировать AI-коуча и сохранить контекст между разговорами
process: Telegram-интерфейс и автоматические Markdown summary
tools:
  - Telegram
  - Markdown
  - AI coach
result: Постоянно используемый коуч-бот с файловой памятью
behavior_shift: От отдельных чатов к собственному интерфейсу и накоплению памяти
limitations: Организаторский шеринг без технического артефакта
---

# Telegram-коуч с памятью в Markdown

<!-- evidence:start -->
## Evidence

### 1. GCONF / AI LOVERS · Telegram · 2026-05-23

- **Автор:** GCONF / AI LOVERS
- **Роль:** `primary`
- **Подтверждает:** Организаторский шеринг персонализированного коуч-бота участницы
- **Visibility:** `public`

> я сделала коуч-бота на основе диминого промта, но немножко его под себя сделала.
>
> он у меня сидит в telegram, то есть мне теперь не нужен chat gpt или claude. я просто через telegram общаюсь с этим коучем. он точно так же помнит контекст, если не лучше.
>
> после каждого разговора он делает короткий md-файл саммари автоматом

- Locator: `telegram:1633415027:1001`
- [Открыть источник](https://t.me/gptlovers/1001)
- Local source: `telegram/GCONF : AI LOVERS - All Time.json`

<!-- evidence:end -->
