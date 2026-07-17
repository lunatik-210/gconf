---
type: "claim"
id: "claim-benchmark-leaderboards-require-method-audit"
label: "Benchmark-лидерство нельзя читать без аудита методологии"
status: "inference"
review_status: "candidate"
first_seen: "2026-07-08"
last_seen: "2026-07-08"
source_wave: "external"
evidence: ["web:openai:separating-signal-from-noise-coding-evaluations:41408bfb0824"]
evidence_quotes: [{"locator":"web:openai:separating-signal-from-noise-coding-evaluations:41408bfb0824","role":"primary","quote":"Our findings point to the difficulty of curating hard but fair benchmarks and the growing utility of agents for scalable data quality checks. In light of these results, we estimate that ~30% of SWE-bench Pro tasks are broken, and advise that model developers carefully examine results.","supports":"Подтверждает существенные проблемы конкретного coding benchmark и необходимость проверки результатов."}]
related: ["pain-agent-output-validation", "technology-gpt-5-6", "technology-claude-sonnet-5", "technology-kimi-k3", "technology-glm-5-2"]
event_context: []
claim_text: "Сравнивать frontier-модели следует по одинаковому прикладному сценарию и полной методологии, а не по одной launch-таблице."
---

# Benchmark-лидерство нельзя читать без аудита методологии

Один официальный аудит не обесценивает все benchmarks, но делает обязательной проверку состава задач, harness, reasoning effort и token budget.

<!-- evidence:start -->
## Evidence

### 1. OpenAI · Web · 2026-07-08

- **Автор:** OpenAI
- **Роль:** `primary`
- **Подтверждает:** Подтверждает существенные проблемы конкретного coding benchmark и необходимость проверки результатов.
- **Visibility:** `public`

> Our findings point to the difficulty of curating hard but fair benchmarks and the growing utility of agents for scalable data quality checks. In light of these results, we estimate that ~30% of SWE-bench Pro tasks are broken, and advise that model developers carefully examine results.

- Locator: `web:openai:separating-signal-from-noise-coding-evaluations:41408bfb0824`
- [Открыть источник](https://openai.com/index/separating-signal-from-noise-coding-evaluations/)
- Local source: `Web Articles/OpenAI/separating-signal-from-noise-coding-evaluations/2026-07-17/article.md`

<!-- evidence:end -->
