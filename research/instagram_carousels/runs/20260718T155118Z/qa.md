# QA — GCONF carousel v7

## Result

Six final carousel images were generated in the only active format: `4:5`,
`1080×1350`. The historical blue originals were preserved and entered image
generation only through checksum-linked grayscale derivatives. The old v6 run
was not changed.

## Reflection incorporated

- The master-frame owns the warm-paper grid, coral palette, margins, header,
  and pagination. No code-owned header overlay was used.
- Exact-resize normalization preserves all four generated edges. The earlier
  cover crop was retired after it reproducibly removed the header from a
  near-4:5 raw image.
- Grayscale prevents blue palette leakage but does not erase old meaning. A
  rejected program-slide attempt copied `8 разделов и 60+ материалов` from the
  historical reference. The agent now marks every readable word, number,
  attribution and claim in Image 2 as forbidden legacy-content unless present
  in the current copy inventory.
- Header glyph measurement no longer includes the divider line. The measured
  right-anchor deltas are `-13, +6, -7, -4, +8, +8 px`; the configured honest
  tolerance is 14 px. Vertical baselines remain within 3 px.
- Content-end detection counts both graphite and muted-coral content so a
  coral price row is not mistaken for empty space.

## Per-slide visual and copy audit

1. **Cover** — `Vibe Coding` appears once; `AI Ops`, transition, three system
   ideas, date, duration and price are present. Header visible. Full-height use.
2. **За 3 недели** — all five outcomes are present. Small coral number markers;
   no blue; no meaning removed.
3. **Программа** — all six full blocks are present in a 2×3 grid. No leaked
   legacy statistic. The revised plain-language setup block is preserved.
4. **Запросы** — mandatory heading and all six current audience requests are
   present. No old professions, countries or invented attribution.
5. **Результат** — six case cards are present under `С чем уходят участники
   GCONF`; individual origins and the old caveat are absent from public art.
6. **Старт** — exact confirmed CTA `«vibe» в комменты — скинем детали`, four
   tags, date, duration and both prices are present. No placeholder remains.

## Automated checks

- dimensions: six of six `1080×1350`;
- mixed sizes: none;
- electric-blue pixels: `0` on every slide;
- vertical fill: `0.834–0.954`;
- content end: `1174–1276`;
- header report: pass;
- visual-style report: pass;
- source and derivative SHA provenance: recorded.

## GCONF voice audit

- Voice mode: `GCONF`; address: `вы`.
- Behavioral transition: from a one-off working agent to a repeatable AI
  operating practice.
- Audience tension: access/setup friction, lost context, unsafe permissions,
  repeated mistakes and uncertainty about the first useful process.
- Evidence: current v7 writing source and its evidence ledger remain the copy
  baseline; historical images are used only for composition.
- Primary CTA: `«vibe» в комменты — скинем детали`.
- No generic “AI changes everything” language, new speakers, guarantees or
  unsupported metrics were introduced.

## Publication status

`publication_ready: false`. The date remains a user-authorized editorial
proposal, and permissions for sensitive participant cases still need review.
