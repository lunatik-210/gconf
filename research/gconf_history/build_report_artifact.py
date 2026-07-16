#!/usr/bin/env python3
"""Package the GCONF history analysis as a canonical report artifact."""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPORT_MD = HERE / "GCONF_history_report.md"
TIMELINE_CSV = HERE / "launch_timeline.csv"
ARTIFACT_JSON = HERE / "artifact.json"


def slugify(text: str) -> str:
    value = re.sub(r"[^a-zA-Zа-яА-Я0-9]+", "-", text.lower()).strip("-")
    return value[:60] or "section"


def split_markdown(markdown: str) -> list[dict]:
    lines = markdown.splitlines()
    title = lines[0].strip()
    blocks = [{"id": "title", "type": "markdown", "body": title, "layout": "full"}]
    current = []
    current_heading = ""
    for line in lines[1:]:
        if line.startswith("## "):
            if current and any(part.strip() for part in current):
                blocks.append(
                    {
                        "id": slugify(current_heading),
                        "type": "markdown",
                        "body": "\n".join(current).strip(),
                        "layout": "full",
                    }
                )
            current_heading = line[3:].strip()
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(
            {
                "id": slugify(current_heading),
                "type": "markdown",
                "body": "\n".join(current).strip(),
                "layout": "full",
            }
        )
    return blocks


def main() -> None:
    generated_at = datetime.now(timezone.utc).isoformat()
    report_markdown = REPORT_MD.read_text(encoding="utf-8")
    blocks = split_markdown(report_markdown)
    for block in blocks:
        if block["id"].startswith("хронология"):
            block["body"] = re.sub(
                r"\n\| Версия \|.*?\n\n(?=Первый разрыв)",
                "\n\n",
                block["body"],
                flags=re.S,
            )

    timeline = list(csv.DictReader(TIMELINE_CSV.open(encoding="utf-8")))
    timeline_rows = []
    cadence_rows = []
    for row in timeline:
        days = int(row["days_since_previous"]) if row["days_since_previous"] else None
        item = {
            "label": row["label"],
            "start": row["start"],
            "days_since_previous": days,
            "positioning": row["positioning"],
            "status": row["status"],
            "announcement_id": int(row["announcement_id"]),
            "announcement_date": row["announcement_date"],
        }
        timeline_rows.append(item)
        if days is not None and row["status"] not in {"fact_experiment", "fact_upcoming"}:
            cadence_rows.append(item)

    def sql_literal(value) -> str:
        if value is None:
            return "NULL"
        if isinstance(value, int):
            return str(value)
        return "'" + str(value).replace("'", "''") + "'"

    cadence_values = ",\n  ".join(
        "("
        + ", ".join(
            sql_literal(row[field])
            for field in [
                "label",
                "start",
                "days_since_previous",
                "positioning",
                "status",
                "announcement_id",
            ]
        )
        + ")"
        for row in cadence_rows
    )
    analysis_sql = (
        "WITH launch_cadence(label, start, days_since_previous, positioning, "
        "status, announcement_id) AS (\n  VALUES\n  "
        + cadence_values
        + "\n)\nSELECT * FROM launch_cadence ORDER BY start;"
    )

    # Put the cadence explanation and visual immediately after the timeline narrative.
    insert_at = next(
        (
            index + 1
            for index, block in enumerate(blocks)
            if block["id"].startswith("хронология")
        ),
        3,
    )
    blocks[insert_at:insert_at] = [
        {
            "id": "cadence-explanation",
            "type": "markdown",
            "body": (
                "### Ритм запусков стал частью продукта\n\n"
                "После периода поиска между первым и вторым потоками основные "
                "запуски стабилизировались: большинство интервалов укладывается "
                "в 63–70 дней. График показывает дни между стартами; "
                "экспериментальный AI weekend и ещё не начавшийся июльский поток "
                "исключены, чтобы не смешивать основной цикл с тестовым форматом."
            ),
            "layout": "full",
            "sourceId": "analysis",
        },
        {
            "id": "cadence-chart-block",
            "type": "chart",
            "chartId": "launch-cadence",
            "layout": "full",
        },
        {
            "id": "timeline-table-block",
            "type": "table",
            "tableId": "launch-timeline",
            "layout": "full",
        },
    ]

    sources = [
        {
            "id": "public-channel",
            "label": "GCONF / AI LOVERS — Telegram export",
            "href": "https://t.me/gptlovers",
            "query": {
                "description": (
                    "Публичные анонсы, кейсы, программы и постфактум-рефлексии "
                    "из полного Telegram-экспорта."
                ),
                "language": "json",
                "tables_used": ["GCONF : AI LOVERS - All Time.json"],
                "filters": ["type = message", "2023-06-14 through 2026-07-13"],
                "executed_at": generated_at,
            },
        },
        {
            "id": "community",
            "label": "ИИ-сообщество GCONF — private Telegram export",
            "query": {
                "description": (
                    "Органические сообщения выпускников, кейсы, вопросы и "
                    "обсуждения из закрытого сообщества."
                ),
                "language": "json",
                "tables_used": ["ИИ-сообщество GCONF - All Time.json"],
                "filters": ["type = message", "2024-11-14 through 2026-07-05"],
                "executed_at": generated_at,
            },
        },
        {
            "id": "analysis",
            "label": "Reproducible GCONF history analysis",
            "query": {
                "engine": "sqlite",
                "sql": analysis_sql,
                "description": (
                    "Реконструкция запусков, расчёт интервалов и отбор "
                    "evidence-сообщений из двух Telegram-экспортов."
                ),
                "language": "sql",
                "tables_used": [
                    "GCONF : AI LOVERS - All Time.json",
                    "ИИ-сообщество GCONF - All Time.json",
                ],
                "metric_definitions": [
                    "days_since_previous = calendar days between stated launch dates",
                    "main cadence excludes the experimental AI weekend and the upcoming July 27 launch",
                ],
                "executed_at": generated_at,
            },
        },
    ]

    artifact = {
        "surface": "report",
        "manifest": {
            "version": 1,
            "surface": "report",
            "title": (
                "Как развивался GCONF: запуски, аудитория, кейсы "
                "и механизм следующего анонса"
            ),
            "description": (
                "Источник-подтверждённая история GCONF по публичному каналу "
                "и закрытому сообществу выпускников."
            ),
            "generatedAt": generated_at,
            "sources": sources,
            "blocks": blocks,
            "charts": [
                {
                    "id": "launch-cadence",
                    "title": "Интервалы между основными запусками GCONF",
                    "subtitle": (
                        "Календарные дни между стартами; основной цикл без "
                        "экспериментального weekend и будущего запуска"
                    ),
                    "showDescription": True,
                    "intent": "comparison",
                    "question": "Насколько стабилен ритм запусков GCONF?",
                    "rationale": (
                        "Вертикальные столбцы позволяют сравнить дискретные "
                        "интервалы между отдельными когортами без ложной "
                        "непрерывности."
                    ),
                    "type": "bar",
                    "dataset": "cadence",
                    "sourceId": "analysis",
                    "encodings": {
                        "x": {"field": "label", "type": "nominal", "label": "Запуск"},
                        "y": {
                            "field": "days_since_previous",
                            "type": "quantitative",
                            "label": "Дней после предыдущего старта",
                            "unit": "дней",
                        },
                        "tooltip": [
                            {"field": "start", "type": "temporal", "label": "Старт"},
                            {
                                "field": "positioning",
                                "type": "text",
                                "label": "Позиционирование",
                            },
                            {
                                "field": "days_since_previous",
                                "type": "quantitative",
                                "label": "Интервал",
                                "unit": "дней",
                            },
                        ],
                    },
                    "layout": "full",
                    "maxRows": 20,
                }
            ],
            "tables": [
                {
                    "id": "launch-timeline",
                    "title": "Карта запусков и основных обещаний",
                    "subtitle": (
                        "Подтверждённые и реконструированные версии с октября "
                        "2023 по июль 2026"
                    ),
                    "dataset": "timeline",
                    "defaultSort": {"field": "start", "direction": "asc"},
                    "density": "spacious",
                    "sourceId": "analysis",
                    "layout": "full",
                    "columns": [
                        {"field": "label", "label": "Версия", "type": "text"},
                        {"field": "start", "label": "Старт", "type": "date"},
                        {
                            "field": "days_since_previous",
                            "label": "Интервал, дней",
                            "format": "number",
                        },
                        {
                            "field": "positioning",
                            "label": "Основное обещание",
                            "type": "text",
                        },
                        {
                            "field": "status",
                            "label": "Статус привязки",
                            "type": "text",
                        },
                        {
                            "field": "announcement_id",
                            "label": "Message ID",
                            "format": "number",
                        },
                    ],
                }
            ],
        },
        "snapshot": {
            "version": 1,
            "generatedAt": generated_at,
            "status": "ready",
            "datasets": {
                "cadence": cadence_rows,
                "timeline": timeline_rows,
            },
        },
        "sources": sources,
    }
    ARTIFACT_JSON.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(ARTIFACT_JSON)


if __name__ == "__main__":
    main()
