# Processing contract

`knowledge/processing/<scope-id>/` contains committed Obsidian markers for
logical evidence batches. These cards are the durable processed/not-processed
state. Do not create a document-level ledger.

## Fingerprint

Compute SHA-256 over sorted lines containing `locator`, a NUL separator, and
the current checksum for every selected document and transcript chunk. A
missing card is `pending`; a matching fingerprint is `complete`; a different
fingerprint is `stale`.

The semantic profile version is part of completion state: a matching
fingerprint created with an older profile remains `stale`.

`prepare` writes ephemeral work units under `knowledge/runs/insight-extract/`.
`finalize` must find the latest prepared fingerprint, recompute it, validate
every output card and evidence locator, and only then write the processing
card. Every listed output must contain at least one evidence locator from that
batch, although it may consolidate evidence from other batches. SQLite
rebuilds must not remove processing cards.

## Processing card

Use JSON-compatible inline arrays in frontmatter:

```yaml
---
type: insight_processing
scope_id: "next-gconf"
batch_id: "internal-community-after-may"
processing_status: "complete"
profile_version: "semantic-v2-human-evidence"
window_start: "2026-05-25"
window_end: "2026-07-17"
input_fingerprint: "..."
document_count: 42
chunk_count: 0
processed_at: "2026-07-17T15:30:00Z"
outputs: ["pain-agent-context-chaos"]
---
```

Do not finalize a batch merely because a work-unit extraction failed. Empty
outputs mean the complete batch was reviewed and contained no reusable signal.
