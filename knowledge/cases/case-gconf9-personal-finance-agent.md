---
type: case
id: case-gconf9-personal-finance-agent
label: Финансовый агент работает с десятью годами реальных данных
status: fact
review_status: approved
first_seen: 2026-01-29
last_seen: 2026-01-29
source_wave: internal
evidence:
  - telegram:2573352710:2968
evidence_quotes:
  - locator: telegram:2573352710:2968
    role: primary
    quote: |-
      Наконец то дошли руки освоить CustomGPT. Сделал своего ИИ-агента финансиста. В связке сервисом трекинга финансов теперь внутри ChatGPT могу работать со своими реальными данными:
      - создавать голосом расходы
      - задавать свободный вопрос, например: "как соотносятся доходы по бизнесу за 2025 и личные траты, дай инсайты и советы" 

      Я больше 10 лет веду учёт через ZenMoney. Там все банковские счета подключены, что то через пуш и sms подтягивается. И у них есть API для доступа.
    supports: Прямое описание агента, данных и доступных действий
related:
  - cohort-gconf-9-vibe-coding-sep-2025
event_context:
  - event_id: cohort-gconf-9-vibe-coding-sep-2025
    phase: after
    attribution: unattributed
case_origin: gconf_community
reporting_mode: direct_self_report
proof_level: described_result
artifact_status: working
initial_task: Вносить расходы голосом и анализировать реальные личные и бизнес-финансы
process: CustomGPT подключён к API ZenMoney
tools:
  - CustomGPT
  - ChatGPT
  - ZenMoney
result: Агент создаёт расходы и отвечает на свободные вопросы по реальным данным
behavior_shift: Десятилетний финансовый архив стал разговорным рабочим контекстом
limitations: Не описаны права доступа и контроль безопасности
---

# Финансовый агент работает с десятью годами реальных данных

<!-- evidence:start -->
## Evidence

### 1. Gconf #9 | Vibe Coding · Telegram · 2026-01-29

- **Автор:** Alexey Korsakov
- **Роль:** `primary`
- **Подтверждает:** Прямое описание агента, данных и доступных действий
- **Visibility:** `internal`

> Наконец то дошли руки освоить CustomGPT. Сделал своего ИИ-агента финансиста. В связке сервисом трекинга финансов теперь внутри ChatGPT могу работать со своими реальными данными:
> - создавать голосом расходы
> - задавать свободный вопрос, например: "как соотносятся доходы по бизнесу за 2025 и личные траты, дай инсайты и советы" 
>
> Я больше 10 лет веду учёт через ZenMoney. Там все банковские счета подключены, что то через пуш и sms подтягивается. И у них есть API для доступа.

- Locator: `telegram:2573352710:2968`
- [Открыть источник](https://t.me/c/2573352710/2968)
- Local source: `telegram/Gconf #9 | Vibe Coding.json`

<!-- evidence:end -->
