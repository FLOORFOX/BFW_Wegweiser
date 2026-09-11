# Graphic & Floor Plan Strategy

State: 2026-09-11

## 1. Principle: One Semantic SVG per Floor

A single SVG per floor serves two consumers at once:

- **Visual layer** — the floor plan rendered in the kiosk ([web/index.html](../web/index.html)).
- **Topology layer** — zones and portals parsed by the offline compiler ([src/main.py](../src/main.py)).

Both consume the same `viewBox`, so route overlays and geometry are locked to a
shared coordinate space by construction. No projection adapters, no drift.

This preserves the boundary set in [docs/adr.md](adr.md): Python compiles,
the browser only looks up and renders.

```text
[Messy plan: photo / PDF / Lageplan]
        │  Claude Design (hybrid, supervised)
        ▼
[Semantic SVG per floor]  ──────────────► web/assets/  (visual layer)
        │  parser + validate_plan.py
        ▼
[topology.json: zones, portals, obstacles]
        │  src/main.py (state search over the dual graph)
        ▼
[web/data.json + web/data.js]  ─────────► O(1) lookup, <polyline> overlay
```

## 2. Data Model: Zones and Portals

The asset encodes the **dual graph** fixed by [docs/axioms.md](axioms.md) and
[docs/glossary.md](glossary.md), which supersedes the flat coordinate lists
currently hardcoded in [src/main.py](../src/main.py):

| Concept | SVG carrier | Meaning |
| :--- | :--- | :--- |
| Zone | `<polygon>` / `<rect>` / `<path>` with `id`, `data-kind`, `data-label` | A space: room, corridor, hall, stairwell, or service area |
| Portal | `<circle>` with `id`, `data-a`, `data-b` | A boundary between **exactly two** zones; carries the routing coordinate |
| Obstacle | shape with `data-zone` | A non-walkable fixture inside a zone: counter, booth, seating, atrium void |
| Exterior | reserved zone id `aussen` | Building egress; anchors entrances |
| Floor link | `data-kind="stairs"` / `elevator` | Vertical transition, weighted separately |

Only the portal record is authored. The zone index (zone → its portals) and the
segment list (all portal pairs within a zone) are **derived by inversion**
(axioms 5–6) and must never be written by hand.

**Axiom 4 is the zone test:** within a zone, every portal must be directly
reachable from every other. If it is not, it is not one zone — split it with a
virtual portal. This is the only rule needed for data entry; no zone categories
are required.

A portal need not be a door. A doorless opening, or a line drawn across a
corridor at a corner, is equally a portal. Two portals between the same pair of
zones are kept separate only when the choice between them changes a route —
adjacent double doors merge into one.

`data-kind` doubles as the accessibility filter for step-free routing: excluding
`stairs` requires no separate graph.

## 3. Authoring Contract (non-negotiable for parseability)

1. **Zero transforms on routing groups.** `#zones`, `#portals` and `#obstacles`
   must have no `transform` attribute; coordinates are absolute in `viewBox`
   space. Presentation padding belongs in CSS or an outer wrapper, never on data
   groups.
2. **Layer separation by group id:** `#shell`, `#zones`, `#portals`,
   `#obstacles`, `#labels`, `#decor`, `#legend`. Only the first four are parsed;
   `#legend` and `#decor` are stripped or CSS-hidden in the kiosk build.
3. **Stable ids** per [docs/glossary.md](glossary.md). Zone ids are printed room
   numbers (`E.54a`, `R.58`) or lowercase ASCII slugs (`flur_nord`, `atrium`);
   `aussen` is reserved for the exterior; portal ids are sequential (`p01`) and
   must not be renumbered once published. Labels are German as printed on the
   plan.
4. **Every portal references exactly two existing zone ids** via `data-a` /
   `data-b` (or the reserved `aussen`), and never the same zone twice. Dangling
   references fail the build.
5. **Every zone has at least one portal**, and its two zones must share a wall,
   not merely a corner.
6. **No metadata blobs.** Strip C2PA / editor metadata before the file enters
   [web/assets](../web/assets).
7. **Uniform `viewBox` per floor** so multi-floor layers stack without rescaling.

The contract is machine-checked by `validate_plan.py`, which additionally
verifies axiom 4 (zone convexity as a proxy for unhindered reachability), axiom 1
(no overlapping zones), and graph connectivity.

## 4. Execution Phasing

### Phase A — Hybrid AI Vectorization (current)

Tool: **Claude Design**, operated in supervised hybrid mode.

1. Submit the source material (emergency plan photo, `Lageplan EG` PDF) with the
   authoring contract from Section 3 as explicit instructions.
2. The model emits a schematic SVG: simplified geometry, wall thickness, door
   leaves, furniture and dimensions removed; zones and portals tagged.
3. **Human supervision is mandatory and is the quality gate.** Verify against the
   source: room numbering, adjacency correctness, portal placement at real door
   positions, corridor connectivity, missing rooms.
4. Correct by direct SVG edit or by iterating with the model; normalize
   transforms, strip metadata and chrome.
5. Commit the reviewed floor SVG to [web/assets](../web/assets).

Source hierarchy: the `Flucht- und Rettungsplan` (2026) supersedes the
`Lageplan EG v1.2` (2018) wherever they disagree — room numbering has drifted
and the personal names on the older plan are stale. The Lageplan remains
authoritative for wing layout and overall geometry.

Architectural door notation matters when reading the source: a door is a line
plus a quarter-circle arc. Solid black blocks are wall thickness, not doors —
misreading them produces doubled portals.

Rationale: this collapses the former "trace walls, then place nodes, then
transcribe coordinates" sequence into a single supervised pass, and it scales to
further floors and wings without per-floor manual drafting.

Residual risk: the model infers geometry it cannot read from a blurry source.
Mitigation is review discipline, not tooling — every zone and portal is checked
against the official plan before it is trusted for routing.

### Phase B — SVG Ingestion (next)

A parser module in [src](../src) using the standard library:

- Reads `#zones` → zone table with `id`, `kind`, `label`, geometry.
- Reads `#portals` → the portal record: coordinates plus the zone pair.
- Reads `#obstacles` → fixtures excluded from the movement zone.
- Derives the zone index and segment list by inversion; never reads them from
  the file.
- Emits `topology.json`, replacing the hardcoded `nodes` / `checkpoints` /
  `connections` dicts in [src/main.py](../src/main.py).
- Runs `validate_plan.py` and fails loudly on contract violations.

### Phase C — Full Automation (deferred)

Only if plan volume justifies the investment: OpenCV pre-processing (HSV masking
of emergency pictograms, morphological cleanup, binarization) feeding an
auto-tracer, plus post-processing (path simplification, orthogonal snapping,
`svgo`). Explicitly out of scope while supervised hybrid output is sufficient.

## 5. Compilation and Rendering

Within the boundary set by [docs/adr.md](adr.md) — Python compiles, the browser
only looks up and renders:

- [src/main.py](../src/main.py) loads `topology.json`, derives the zone index and
  segment list, applies the cost model, searches the state graph, and exports
  [web/data.json](../web/data.json) / [web/data.js](../web/data.js).
- **The export contract changes.** Queries are zone to zone, so `destinations`
  becomes zone ids and a route becomes the canonical alternating sequence
  `zone₁ portal₁ zone₂ … portalₙ zoneₙ₊₁`. [web/script.js](../web/script.js)
  resolves portal coordinates from that sequence for the `<polyline>`.
- [web/index.html](../web/index.html) inlines the floor SVG and draws the route
  into the same `viewBox`; `data-kind` and zone ids become CSS hooks for
  destination highlighting.
- Multi-floor: one `<g id="floor:eg">` per floor, toggled by CSS; vertical
  portals connect them.

Verification loop: edit SVG → run `python src/main.py` → reload kiosk.

## 6. Options Evaluated (reference)

| Approach / Tool | Pros | Assessment |
| :--- | :--- | :--- |
| **Claude Design, supervised hybrid** *(chosen)* | Produces semantically tagged SVG (zones, portals, kinds) in one pass; no drafting skill required; scales across floors | Requires disciplined human verification against source plans |
| Inkscape manual tracing | Free, offline, unlimited, pristine human-verified geometry | Sound fallback; per-floor drafting effort, and topology must be added separately |
| Automated image-to-vector *(Autotracer, Vectorization.org, Trace Bitmap)* | Fast, no drawing | Vectorizes text, pictograms and smudges; jagged double-walled paths; unusable node counts |
| Paint pre-clean + auto-trace | Avoids vector tooling | Still squiggly and double-walled; erasing clutter costs as much as drawing walls |
| OpenCV filter pipeline | Scales to many plans | Hours of tuning; deferred to Phase C |
| Sweet Home 3D / Floorplanner | Polished 2D/3D layouts | Free tiers capped (projects/floors); CAD overhead; messy SVG export |
| Figma / Miro | Quick schematics | Not fully free, account-bound; nested transforms and clip paths in export |
| Graph data encoded by hand in a drawing editor | Single file | Editors rewrite ids and inject transforms; visual edits break the parser — solved here by generating the SVG programmatically instead |
