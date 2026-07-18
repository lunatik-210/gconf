---
name: gconf-instagram-carousel-designer
description: Generate a six-image 4:5 GCONF Instagram carousel from approved copy by first creating one approved 1080×1350 blank master-frame, then independently editing that same frame for every slide with grayscale structural derivatives of the historical references. Use when header stability, text completeness, palette isolation, balanced vertical fill, reference traceability, and cross-slide geometry must be validated. Do not use to rewrite strategy, invent unapproved cohort facts, publish, or modify source references.
---

# GCONF Instagram Carousel Designer

Turn approved slide copy into six coherent raster assets. Treat the feed and
previous carousel as a design system, not a template to clone.

## Run the workflow

1. Read repository `AGENTS.md`, the complete `$imagegen` skill, this skill's
   `references/design-system.md`, and `references/output-contract.md`.
2. Inspect every local reference with `view_image` before generation:
   - the full-feed screenshot;
   - all six previous carousel slides;
   - any additional image explicitly supplied by the user.
3. Require a confirmed `announcement_copy_approval` decision from
   `$gconf-editorial-gates` that binds the exact carousel Markdown SHA. If the
   user explicitly approves the copy in the current instruction, record the
   decision first; otherwise ask and stop. Also require a confirmed
   `publication_permission` decision for the writer run. Prepare a read-only
   design packet:

```bash
python3 -B .agents/skills/gconf-instagram-carousel-designer/scripts/prepare_design_context.py \
  --announcement-run research/announcement_drafts/runs/RUN_ID \
  --decision-id DECISION_ID \
  --permission-decision-id PERMISSION_DECISION_ID \
  --carousel-file instagram-carousel.md \
  --references-dir 'Instagram/Прошлый Анонс'
```

The only supported format is `4:5` / 1080×1350. Do not expose an aspect-ratio
choice or mix dimensions inside one run.

4. Create grayscale structural derivatives of the feed screenshot and all six
   historical slides with `scripts/prepare_structure_references.py`. Preserve
   originals, and record source/derived paths and SHA values. Only grayscale
   derivatives may enter image-generation calls.
5. Choose one new primary highlighter color by comparing recent launches in
   the feed. Preserve black, warm white, grid, and utilitarian grey. Reject a
   primary color that visually repeats the immediately previous launch.
6. Write `design-brief.json` with the exact palette, typography hierarchy,
   grid, slide jobs, copy source SHA, copy inventory, required text units,
   prompt per slide, and placeholder treatment. A visual edit must be explicit;
   otherwise preserve every semantic unit verbatim.
7. Generate `master/slide-00-master.png` with built-in `image_gen`, using the
   grayscale feed, grayscale cover, and approved launch palette reference. It must be a blank
   1080×1350 frame containing only warm-paper/grid styling and the visible
   header `[ gconf ]` — `01 / 06`; no large title or content. Normalize it once,
   inspect it with `view_image`, record its SHA and header geometry, and stop if
   it is not approved. Never create or repair the header with a code overlay.
8. Use built-in `image_gen` once per slide in edit mode. Each call receives only
   two roles: the same `slide-00-master.png` as the edit target and the matching
   grayscale historical slide as the structure/density/geometry reference. Image 1
   owns every color; Image 2 owns no color. Every readable word, number, name,
   geography, attribution or claim in Image 2 is legacy-content and forbidden
   unless it also appears in the current copy inventory. Change the requested
   mini-title and pagination, then fill the content zone. Never use one generated
   slide as the source for another. Record path and SHA for all blue references.
9. Require a clean 4:5 editorial card, Cyrillic grotesk, 80–96 px
   margins, no photos unless the brief requires one, no gradients, no fake UI
   chrome, no watermark, and no invented copy. Treat the matching old slide as
   a geometry contract: the main content must begin immediately below its
   original metadata row. Preserve the master header baseline and right anchor;
   never create a second empty band beneath it.
10. Save every selected raw output under
   `research/instagram_carousels/runs/<UTC-run-id>/source/`. Never leave a
   project asset only under `$CODEX_HOME/generated_images/`.
11. Exact-normalize each selected edit directly into `generated/` at 1080×1350
   with `scripts/normalize_carousel.py`. Do not call `apply_shared_header.py` or perform any
   header compositing, painting, cropping, or post-generation text replacement.
12. Inspect all six final images with `view_image`. Reject illegible,
    misspelled, duplicated, cropped, or stylistically drifting slides. Iterate
    one slide at a time with a single targeted correction.
13. Run:

```bash
python3 -B .agents/skills/gconf-instagram-carousel-designer/scripts/validate_carousel.py \
  research/instagram_carousels/runs/RUN_ID
```

14. Report palette, six final paths, prompt set, generation mode, and remaining
publication blockers. Ask the human to approve or reject all six final images;
record an approval as `carousel_visual_approval` bound to the six image SHA
values. Never interpret successful QA as visual approval.

## Preserve editorial truth

- Use only the supplied slide copy or a visual edit explicitly recorded
  in the design brief. Do not add dates, cohort numbers, speakers, guarantees,
  metrics, scarcity, or CTA destinations.
- Render an unknown date as `СТАРТ — СКОРО` and an unknown CTA as
  `ДЕТАЛИ И ЗАПИСЬ — СКОРО` only when producing a teaser-shaped review asset.
  Record this as editorial placeholder handling, not a verified cohort fact.
- Keep sensitive cases and permission decisions inherited from the announcement
  run. Do not introduce new cases during design.
- Preserve exact participant quotations when used. Do not repair their wording.
- On slides 2, 3, 5, and 6, change only line breaks and typography unless a
  human explicitly approves a `visual_edit`. Never solve overflow by deleting
  a result, explanation, request, case, origin, condition, or tag.
- Put every required text unit verbatim in its slide prompt. Validation fails
  when a required unit is absent even if the item count looks correct.

## Keep the carousel coherent

Use one palette, one grid, and one heading family. The approved master-frame
owns the monospaced metadata and counter geometry. Dense-slide headings use at most 12–15% of
height; body copy targets 30–36 px at 1080 px width and origins 25–30 px. If
space is tight, reduce type size and gaps before touching copy. Avoid condensed
uppercase for every subheading. The cover and final conditions slide may use the primary color on
up to 25% of the canvas; information slides use it on at most 10–15%.

Do not imitate another brand, add generic AI imagery, or turn the carousel into
futuristic neon art. GCONF should look editorial, practical, human, and slightly
experimental.

For 4:5, enforce large-title zones y=210–330 on the cover, y=150–240 on
slides 2–5, and y=200–330 on the final conditions slide. Require the final
meaningful content row at y=1160–1290 so the layout uses the full canvas.
Dark-pixel title
detection may use at most 12 px of antialiasing tolerance without changing
those design targets. Fail when the header
baseline moves more than 8 px vertically, its left/right anchors move more than
14 px, electric-blue pixels appear, coral exceeds the slide allowance, or a
second blank region appears beneath it.
