# Carousel output contract

Create `research/instagram_carousels/runs/<UTC-run-id>/` with:

- `design-brief.json`;
- `prompts.json` containing six final built-in image-generation prompts;
- `master/slide-00-master.png` and `master-report.json`;
- `source/slide-01.*` through `source/slide-06.*`;
- `generated/slide-01.png` through `generated/slide-06.png`;
- `header-geometry-report.json`;
- `manifest.json`;
- `qa.md`.

Every final image must be 1080×1350, RGB or RGBA, independently openable, and
ordered by its zero-padded filename. A run must never mix dimensions. The six files form one carousel
and use the same palette, external grid, counter, and brand grammar.

`design-brief.json` records the carousel filename and SHA, the copy inventory,
required text units for each slide, explicit `visual_edits`, palette, geometry,
and density rules. `prompts.json` contains six objects with `id`, `prompt`, and
`required_text`; every required unit must occur verbatim in its prompt.

`manifest.json` records source announcement run, source carousel path and SHA,
copy inventory, feed reference, six old-slide references with path and SHA,
the generated master-frame with path and SHA, palette, format, generation
mode (`built-in image_gen`), source/final paths, prompt IDs, image dimensions,
date status, placeholder handling, QA status, and `publication_ready`. It embeds
the master SHA and measured header geometry. Validation compares every generated
header against the generated master with masked background and text-anchor
tolerances; no overlay or code-owned header is allowed.

Record `content_start_y`, `content_end_y`, and vertical fill for every final
slide. Enforce the large title zones from the design system: cover y=210–330,
slides 2–5 y=150–240, and final conditions y=200–330. The last meaningful row
must be at y=1160–1290. Automated dark-pixel detection may use at most
12 px of measurement tolerance for antialiasing; this does not move the design
target. The master header occupies the top area. A second blank buffer is a hard
failure even when all copy is present.

Record every original historical reference and its grayscale derivative with
both SHA values. Reject a prompt that receives a color historical reference.
Record forbidden-blue and coral-pixel counts for each final slide.
Each prompt also records `legacy_reference_policy`; readable text, numbers,
attributions, cohort facts, and claims in a structural derivative are not copy
sources and may appear only when present in the current copy inventory.

Set `publication_ready: false` if unresolved publication permissions remain,
if placeholders were converted into teaser language, or if any generated text
differs from approved copy. `qa.md`
must record per-slide inspection for text accuracy, cropping, hierarchy,
contrast, reference fidelity, and cross-slide consistency.

Schema 2.0 also records the source `announcement_copy_approval` in
`decision_refs`, uses `workflow_status: awaiting_visual_approval`, and keeps
`publication_status: not_ready`. Successful QA never substitutes for a later
`carousel_visual_approval` decision bound to all six generated image SHA values.
