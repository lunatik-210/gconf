# Scope contract

Store project scope configuration at
`knowledge/processing/<scope-id>/scope.json`.

Required top-level fields are `schema_version`, `id`, `profile_version`,
`event_ids`, and `batches`. `event_ids` is the closed list of events that may
appear in semantic `event_context` for this scope. Each batch requires `id`,
`label`, `window_start`, `window_end`, and one or more selectors.

A selector supports:

- `source_ids`: exact SQLite source IDs;
- `kinds`: exact document kinds;
- `window_start` and `window_end`: optional selector overrides;
- `include_chunks`: include transcript chunks for selected documents.
- `topic_root_ids`: include messages belonging to these topic roots
  by following their reply chains;
- `exclude_topic_root_ids`: exclude those topic threads;
- `group_by_thread`: keep Telegram threads together while packing bounded
  work units.

Batch selectors are ORed. Filters within one selector are ANDed. Normalize all
publication dates to `YYYY-MM-DD` before applying inclusive windows. Deduplicate
records by locator.

Prepared Telegram records include `reply_to_locator`,
`thread_root_locator`, `thread_root_title`, and bounded `reply_context` when
available. These provide conversation context; semantic evidence must still
point to exact document locators.

Keep logical batches understandable to an editor. Work units are only bounded
execution pieces and must not become persistent processing markers.
