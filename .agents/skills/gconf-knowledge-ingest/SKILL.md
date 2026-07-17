---
name: gconf-knowledge-ingest
description: Import already-collected GCONF research artifacts into the local SQLite and Obsidian knowledge base. Use when adding or refreshing YouTube research packages, Telegram exports, Instagram exports, or local research files; rebuilding or validating knowledge/, checking ingestion status, or preparing source-backed material for later pain, case, trend, and editorial analysis. Do not use to download, scrape, transcribe, or publish content.
---

# GCONF Knowledge Ingest

Use the bundled CLI for deterministic collection indexing. Keep source collection
in the existing platform skills and keep semantic judgment reviewable.

## Import

```bash
python3 .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py doctor
python3 .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py scan
python3 .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py ingest --all
python3 .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py ingest PATH
python3 .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py search 'агенты OR контекст'
```

The importer:

1. Preserve every source artifact unchanged.
2. Normalize sources, documents, comments, transcript chunks, and reply edges.
   For Telegram, preserve topic-creation documents, nested reply chains, and
   direct public/private message links for later human evidence review.
3. Upsert by stable platform locator and checksum.
4. Rebuild SQLite FTS indexes.
5. Create or refresh generated source cards in `knowledge/sources/`.
6. Record an auditable run report in `knowledge/runs/`.

Read [source-contracts.md](references/source-contracts.md) before changing an
adapter. Read [obsidian-card-contract.md](references/obsidian-card-contract.md)
before creating semantic cards.

## Hand off after import

Use `$gconf-insight-extract` after deterministic import when the user asks to
identify or refresh actors, cohorts, pains, cases, trends, technologies, or
claims. Do not perform semantic extraction inside this skill.

The downstream skill writes candidates directly to typed Obsidian folders,
tracks logical processing batches, and must preserve exact evidence locators.

## Validate and rebuild

```bash
python3 .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py validate
python3 .agents/skills/gconf-knowledge-ingest/scripts/knowledge_ingest.py rebuild
```

`rebuild` deletes only the derived SQLite index and generated source cards, then
reimports local artifacts. It must never delete source exports or approved
semantic cards.

Use `$gconf-youtube-research` before this skill when a YouTube URL has not yet
been collected. This skill must never call yt-dlp, Whisper, or a network API.
