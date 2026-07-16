#!/usr/bin/env python3
"""Build reproducible evidence tables for the GCONF launch-history report."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATH = ROOT / "telegram" / "GCONF : AI LOVERS - All Time.json"
COMMUNITY_PATH = ROOT / "telegram" / "ИИ-сообщество GCONF - All Time.json"
OUT_DIR = ROOT / "research" / "gconf_history"


LAUNCHES = [
    {
        "label": "GCONF 1",
        "start": "2023-11-15",
        "announcement_id": 192,
        "positioning": "10 дней с GPT-евангелистами",
        "status": "fact",
    },
    {
        "label": "GCONF 2",
        "start": "2024-04-15",
        "announcement_id": 291,
        "positioning": "ChatGPT каждый день",
        "status": "fact",
    },
    {
        "label": "GCONF 3",
        "start": "2024-06-17",
        "announcement_id": 474,
        "positioning": "ИИ для помогающих специалистов",
        "status": "fact",
    },
    {
        "label": "GCONF 4",
        "start": "2024-10-07",
        "announcement_id": 516,
        "positioning": "ИИ для маркетологов и контент-мейкеров",
        "status": "fact",
    },
    {
        "label": "GCONF 5",
        "start": "2024-12-10",
        "announcement_id": 561,
        "positioning": "ИИ-воркшоп для предпринимателей",
        "status": "inference",
    },
    {
        "label": "GCONF 6",
        "start": "2025-02-17",
        "announcement_id": 599,
        "positioning": "ИИ как напарник; авторский подход Димы",
        "status": "inference_supported",
    },
    {
        "label": "GCONF 7",
        "start": "2025-04-28",
        "announcement_id": 638,
        "positioning": "ИИ-напарник: BOOST ×10",
        "status": "fact",
    },
    {
        "label": "GCONF 8",
        "start": "2025-07-07",
        "announcement_id": 705,
        "positioning": "AI Life Optimization",
        "status": "inference",
    },
    {
        "label": "GCONF 9",
        "start": "2025-09-15",
        "announcement_id": 737,
        "positioning": "Vibe Coding",
        "status": "fact",
    },
    {
        "label": "Мета-навыки",
        "start": "2025-11-17",
        "announcement_id": 791,
        "positioning": "Системное взаимодействие с GPT",
        "status": "fact_unnumbered",
    },
    {
        "label": "Vibe Coding — январь",
        "start": "2026-01-19",
        "announcement_id": 853,
        "positioning": "Create → Automate → Workspace",
        "status": "fact_unnumbered",
    },
    {
        "label": "Vibe Coding — март",
        "start": "2026-03-23",
        "announcement_id": 910,
        "positioning": "Продукты и автоматизация с AI",
        "status": "fact_unnumbered",
    },
    {
        "label": "AI & Vibe Coding — май",
        "start": "2026-05-25",
        "announcement_id": 977,
        "positioning": "Кодинг-агенты и AI-first процессы",
        "status": "fact_unnumbered",
    },
    {
        "label": "AI weekend",
        "start": "2026-07-04",
        "announcement_id": 1009,
        "positioning": "Первый agentic workflow за 2 дня",
        "status": "fact_experiment",
    },
    {
        "label": "Vibe Coding — июль",
        "start": "2026-07-27",
        "announcement_id": 1040,
        "positioning": "Личная система агентов",
        "status": "fact_upcoming",
    },
]


CASE_IDS = [
    238,
    250,
    257,
    264,
    271,
    278,
    317,
    344,
    414,
    424,
    426,
    433,
    460,
    489,
    622,
    647,
    697,
    718,
    722,
    733,
    736,
    739,
    746,
    779,
    780,
    782,
    783,
    785,
    787,
    789,
    799,
    801,
    815,
    828,
    842,
    850,
    857,
    865,
    896,
    897,
    900,
    926,
    927,
    950,
    990,
    1001,
    1003,
    1008,
    1046,
]


THEMES = {
    "daily_use": r"кажд(ый|ого) день|повседнев|быт|daily|личн(ая|ые|ой|ую) жизнь",
    "business_process": r"бизнес|процесс|команд|продукт|маркетинг|продаж|аналитик|отч[её]т",
    "behavior_change": r"страх|сопротивлен|любопыт|игрив|прокрастин|мышлен|привычк|уверенн|трансформац",
    "community_practice": r"комьюнити|сообществ|практик|встреч|созвон|переопыл|протагонист|поддержк",
    "automation_agents": r"автоматиз|агент|workflow|воркфлоу|n8n|cursor|codex|claude code|openclaw|hermes",
    "content_creation": r"контент|текст|картин|изображен|видео|рилс|маркетолог|копирайтер",
    "meta_skills": r"мета[- ]?навык|контекст|tone of voice|тон общен|партн[её]р|напарник|сотворчеств",
}


TOOLS = [
    "ChatGPT",
    "GPT",
    "Claude",
    "Gemini",
    "Perplexity",
    "Midjourney",
    "Ideogram",
    "Gamma",
    "Make",
    "n8n",
    "Lovable",
    "Supabase",
    "Cursor",
    "Codex",
    "Claude Code",
    "Cowork",
    "OpenClaw",
    "Hermes",
    "NotebookLM",
    "Genspark",
    "Manus",
]


def flatten_text(value) -> str:
    if isinstance(value, str):
        return value
    if not isinstance(value, list):
        return ""
    parts = []
    for item in value:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict):
            text = item.get("text", "")
            href = item.get("href")
            parts.append(f"{text} [{href}]" if href else text)
    return "".join(parts)


def load_messages(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for message in data["messages"]:
        if message.get("type") != "message":
            continue
        rows.append(
            {
                **message,
                "flat_text": flatten_text(message.get("text", "")),
                "day": message["date"][:10],
            }
        )
    return rows


def reaction_score(message: dict) -> int:
    return sum(r.get("count", 0) for r in message.get("reactions", []))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    public = load_messages(PUBLIC_PATH)
    community = load_messages(COMMUNITY_PATH)
    public_by_id = {m["id"]: m for m in public}

    launch_rows = []
    previous_start = None
    for launch in LAUNCHES:
        message = public_by_id.get(launch["announcement_id"], {})
        start = datetime.fromisoformat(launch["start"])
        gap = (start - previous_start).days if previous_start else None
        previous_start = start
        text = message.get("flat_text", "")
        theme_counts = {
            theme: len(re.findall(pattern, text, flags=re.I))
            for theme, pattern in THEMES.items()
        }
        launch_rows.append(
            {
                **launch,
                "announcement_date": message.get("day", ""),
                "days_since_previous": gap,
                "announcement_text": text,
                **theme_counts,
            }
        )

    write_csv(
        OUT_DIR / "launch_timeline.csv",
        list(launch_rows[0].keys()),
        launch_rows,
    )

    announcement_md = ["# Корпус основных анонсов GCONF", ""]
    for row in launch_rows:
        announcement_md.extend(
            [
                f"## {row['label']} — старт {row['start']}",
                "",
                f"Статус привязки: `{row['status']}`. Публичный пост: "
                f"`GCONF / AI LOVERS`, message_id `{row['announcement_id']}`, "
                f"{row['announcement_date']}.",
                "",
                row["announcement_text"].strip() or "_Текст отсутствует в экспорте._",
                "",
            ]
        )
    (OUT_DIR / "announcement_corpus.md").write_text(
        "\n".join(announcement_md), encoding="utf-8"
    )

    case_rows = []
    for case_id in CASE_IDS:
        message = public_by_id.get(case_id)
        if not message:
            continue
        matches = [
            theme
            for theme, pattern in THEMES.items()
            if re.search(pattern, message["flat_text"], flags=re.I)
        ]
        case_rows.append(
            {
                "message_id": case_id,
                "date": message["day"],
                "themes": "|".join(matches),
                "reaction_score": reaction_score(message),
                "text": message["flat_text"],
            }
        )
    write_csv(
        OUT_DIR / "public_case_evidence.csv",
        ["message_id", "date", "themes", "reaction_score", "text"],
        case_rows,
    )

    community_case_pattern = re.compile(
        r"(?i)(мой кейс|новый кейс|принес[лаё].*кейс|задача:|решение:|"
        r"собрал[аи]?|создал[аи]?|автоматизиров|навайбкод|запустил[аи]?|"
        r"сделал[аи]?.{0,80}(бот|приложен|систем|презентац|книг|курс))"
    )
    community_rows = []
    for message in community:
        text = message["flat_text"]
        if len(text) < 180 or not community_case_pattern.search(text):
            continue
        found_tools = [
            tool for tool in TOOLS if re.search(rf"(?i)\b{re.escape(tool)}\b", text)
        ]
        found_themes = [
            theme
            for theme, pattern in THEMES.items()
            if re.search(pattern, text, flags=re.I)
        ]
        community_rows.append(
            {
                "message_id": message["id"],
                "date": message["day"],
                "author": message.get("from", ""),
                "reaction_score": reaction_score(message),
                "themes": "|".join(found_themes),
                "tools": "|".join(found_tools),
                "text": text,
            }
        )
    community_rows.sort(
        key=lambda row: (row["reaction_score"], row["date"]), reverse=True
    )
    write_csv(
        OUT_DIR / "community_case_evidence.csv",
        [
            "message_id",
            "date",
            "author",
            "reaction_score",
            "themes",
            "tools",
            "text",
        ],
        community_rows,
    )

    tool_counts = Counter()
    theme_counts = Counter()
    for row in community_rows:
        tool_counts.update(filter(None, row["tools"].split("|")))
        theme_counts.update(filter(None, row["themes"].split("|")))
    summary = {
        "source_counts": {
            "public_messages": len(public),
            "community_messages": len(community),
            "selected_public_case_messages": len(case_rows),
            "selected_community_case_messages": len(community_rows),
        },
        "community_case_tool_mentions": tool_counts.most_common(),
        "community_case_theme_mentions": theme_counts.most_common(),
        "launches": launch_rows,
    }
    (OUT_DIR / "analysis_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(summary["source_counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
