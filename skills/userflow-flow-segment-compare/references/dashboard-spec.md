# Dashboard spec — flow × segment comparison

The deliverable is a **self-contained HTML file** saved to `/mnt/user-data/outputs/` and presented to
the user. Before writing HTML, read **`userflow-brand-visuals`** (brand look) and **`frontend-design`**
(styling constraints) so it doesn't look templated. Keep everything inline (CSS + JS + data) in one
file so it opens standalone.

## Layout

1. **Header**
   - Content name + type badge (Flow / Announcement)
   - Time window and interval (e.g. "Last 90 days · weekly")
   - The segments being compared, as labeled chips — each chip shows the segment name; ad-hoc ones can
     show their plain-English definition on hover/subtitle.

2. **Comparison table** (the headline view)
   - One **row per segment**, columns = the key metrics for this content type — chosen from what
     `query_flow_metrics` actually returned (see `mcp-metrics.md` → *Metric set by content type*).
     E.g. guide flow → Views · Unique Views · Completions · Completion Rate; announcement → Views ·
     Reactions · Comments; banner → Views · Dismissals; checklist → Started · Completions ·
     Completion Rate. Adapt to the type rather than hardcoding.
   - Right-align numbers; format rates as percentages and counts with thousands separators.
   - Make the leader/laggard per column obvious (e.g. bold or a subtle bar/heat cue in-cell).
   - If a segment is low-sample or zero-data, mark it (a small "low n" / "no data" note) so rates
     aren't misread.

3. **Trend charts** (one per key metric)
   - A single chart per metric with **one line per segment** across the shared time buckets.
   - Consistent color per segment across all charts and the table (a segment is the same color
     everywhere).
   - Clear legend, axis labels, and hover tooltips with the exact value per bucket.
   - Align all series to the same `t` buckets returned by `query_flow_metrics`; fill missing buckets
     as 0 (and, where relevant, note pre-launch periods).

## Charting

Use a lightweight approach that works in a standalone file — inline SVG you generate, or a single
CDN chart library (e.g. Chart.js) loaded via `<script>`. Embed the pulled data directly as a JS
object; do not call the Userflow API from the page. No browser storage.

## Data mapping

- Table rows ← each segment's `items[0].metrics`.
- Trend series ← each segment's `items[0].time_data` (`t` on the x-axis; the metric on the y-axis).
- Keep a single source-of-truth array like:
  `segments = [{ name, color, isAdHoc, definition, metrics, time_data }, ...]`.

## Tone

On-brand, clean, skimmable. The comparison table answers "who performs best" at a glance; the trends
answer "and how is that changing". Don't over-annotate — a short caption per chart is enough.
