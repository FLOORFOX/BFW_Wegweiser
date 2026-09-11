# Architectural decisions

## 1. Offline graph compiler (`src/`) and static presentation client (`web/`)

**Status:** Accepted

**Context:** Deployment targets are a standalone kiosk now, possibly phones
later, with no confirmed hosting budget. The destination scope (entire building)
and optimal routing algorithms are still evolving. Reimplementing the graph
traversal directly in JavaScript (`Wegweiser_Frontend/frontend/script.js`)
already caused logic drift and edge-direction bugs across copies. We need a
clean division of responsibilities and a standard workspace layout that works
out of the box across environments.

**Decision:** Adopt a decoupled two-tier architecture:

- `src/`: Python serves as an offline build tool and graph compiler. It defines
  coordinates, edge weights, and pathfinding rules, precomputing routes and
  exporting static artifacts (`web/data.json` and companion `web/data.js`).
- `web/`: A self-contained static frontend. It performs constant-time lookups
  against the precomputed data and renders SVG paths onto the floor plan,
  containing zero graph traversal or routing algorithms.

Standard directory naming (`src/` and `web/`) is adopted to ensure immediate
compatibility with linters, test runners, and static file servers without custom
path configuration.

Rejected alternatives:

- *Live backend API:* Premature infrastructure and hosting costs; introduces
  runtime network failure modes into offline kiosks.
- *Duplicating pathfinding algorithms in JS:* Causes logic drift and requires
  maintaining identical routing logic in two languages.
- *`builder/` and `viewer/` layout:* Expressive of pipeline roles, but non-standard
  and requires explicit configuration across tooling and test runners.
- *`python/` and `web/` layout:* Categorizes by implementation language rather
  than architectural responsibility.

**Consequences:**

- Zero hosting cost; static files run locally in kiosks (including direct `file://`
  viewing) and can be hosted statically for phones without backend infrastructure.
- Single source of truth for routing algorithms and building data in Python.
- Standard tooling (test discovery, linters, language servers) works without
  custom configuration.
- Future transitions (e.g., Dijkstra, multi-floor transitions, or thin API
  wrappers) only affect `src/`, requiring zero algorithmic changes in `web/`.

## 2. Usage and feedback analytics deferred and decoupled from routing

Status: Accepted

Context: While usage insights (popular destinations, points where users get
confused) will help improve signage and instructions, routing is strictly a
read-only static delivery path. Analytics is fundamentally a write path
(client → collector) that cannot reuse static JSON distribution.

Decision: Defer analytics infrastructure during early development. When
implemented, keep analytics completely decoupled from routing:

- Kiosk phase: local, append-only log files with zero external infrastructure.
- Mobile/hosted phase: a minimal event-collection endpoint or a third-party
  privacy-focused service.
- Privacy by design: never collect or store data traceable to individual users;
  formalize a clear privacy policy before activating any data collection.

Consequences:

- No premature infrastructure or telemetry code built during prototype stages.
- Routing remains completely static, self-contained, and performant regardless of
  analytics decisions.
- Privacy and compliance constraints are established deliberately upfront rather
  than retrofitted.

## 3. Lightweight testing: contract verification and algorithm checks

Status: Accepted

Context: The Python compiler exports static data consumed by a browser viewer.
Testing needs to prevent cross-tier breakage without adding heavy tooling or
slowing prototyping.

Decision: Adopt a minimal, contract-focused test suite:

- Prioritize the contract: Verify `compile_routing_data()` structure, coordinate
  formats, and path coverage (`RoutingContractTests`) to catch frontend-breaking
  schema changes in Python before browser rendering.
- Isolate algorithm tests: Keep graph traversal checks (`PathfindingAlgorithmTests`)
  separate so routing algorithms can change without rewriting export assertions.
- Co-locate in `src/`: Retain tests in `src/test_main.py` under standard unittest
  discovery, deferring a root `tests/` directory until test count warrants it.
- Defer JS tests: Avoid Node.js or npm dependencies while `web/` remains an
  algorithm-free static viewer.

Consequences:

- Schema regressions between compiler and viewer are caught immediately.
- Zero external testing dependencies or build tools required.

## 4. Dual graph: portals as nodes, zone crossings as edges

Status: Accepted

Context: The inherited implementation modelled places as nodes and corridors as
edges. That representation cannot express arrival direction, so "enter north,
leave east" is indistinguishable from "enter west, leave east" and turn costs
require special machinery bolted onto the search. It also cannot express the
project's own premise — a user who knows which room they are in and which room
they want — because its nodes are corridor positions rather than spaces.

Decision: Adopt the dual graph. A **zone** is a space, a **portal** is a
boundary between exactly two zones, and nothing else exists. Portals are nodes,
zone crossings are edges. Search runs over states written
`zone_from | portal | zone_to`, two per portal, with direction carried by the
order. Queries are zone to zone, not point to point.

This is the node-relation graph of the OGC IndoorGML standard, and the same
structure as navmesh portal sequences. The full model is fixed by
[docs/axioms.md](axioms.md) and [docs/glossary.md](glossary.md); the reasoning
is recorded in [docs/design_recap.md](design_recap.md) and the literature
mapping in [docs/convergences.md](convergences.md).

Rejected alternatives:

- *Conventional place-node graph:* cannot express arrival direction; turn
  penalties need separate machinery; the "where am I / where do I want to go"
  premise is inexpressible.
- *Hierarchical three-stretch decomposition (HPA\*):* the original proposal.
  Superseded because the decision-point framing subsumes it — the hierarchy
  becomes the narrative layer for instructions while routing stays table
  lookups. It also loses optimality unless each room connects to every portal in
  its zone and same-zone queries are special-cased.
- *Portals joining more than two zones:* would require a hypergraph, and breaks
  the clean inversion from portal record to zone index.
- *Static zone or portal classification (crossable/terminal, branch/leaf):* not
  derivable from topology; a room with three doors defeats any count-based rule.
  Roles are per-query properties of the route instead.

Consequences:

- Turn costs need no special machinery — direction is already in the state.
- The portal record is the only authored primitive; the zone index and segment
  list are derived by inversion, so they cannot drift from it.
- Search space is bounded at 2 × portal count, which is small by construction
  since only boundaries become nodes.
- Deviation recovery works without extra design: a wrong turn is simply a
  different input to the same stateless function, and portals are named things a
  lost user can report.
- The existing export contract (`start`, `points`, `destinations`, `routes`) is
  a breaking change: destinations become zone ids and routes become canonical
  alternating zone-portal sequences.

## 5. Semantic SVG floor plan as the single source of truth

Status: Accepted

Context: The kiosk draws routes on top of the floor plan, so the graphic asset
and the coordinate data must share one coordinate space or they drift. The
source material is photographed emergency plans and a dated Lageplan —
distorted, cluttered with pictograms and labels, and partly stale. Separately,
building data was hardcoded in [src/main.py](../src/main.py), which does not
scale to ~200–300 zones.

Decision: Author one semantic SVG per floor that serves both consumers. It is
the visual layer rendered in the kiosk and the topology layer parsed by the
compiler: `<g id="zones">` carries zones with `data-kind` and `data-label`,
`<g id="portals">` carries portals with `data-a` and `data-b`, `<g id="obstacles">`
carries non-walkable fixtures. A parser emits `topology.json`, which the
compiler consumes in place of inline dictionaries. Production method and the
full markup contract are specified in
[docs/graphic_strategy.md](graphic_strategy.md).

Rejected alternatives:

- *Separate graphic and topology assets:* avoids editor fragility but
  reintroduces two artifacts that can disagree, and requires maintaining node
  coordinates by hand alongside the drawing.
- *Automated raster-to-vector conversion:* vectorizes text, pictograms and
  smudges indiscriminately; produces jagged double-walled paths unusable for
  styling or coordinate extraction.
- *Raster floor plan with an overlay:* pixelates on high-resolution kiosks and
  offers no CSS hooks for highlighting zones.
- *CAD/BIM formats (DXF, DWG) or GIS stacks (GeoJSON, Leaflet):* heavy
  dependencies and coordinate transformations for a single building.
- *Hosted floor plan editors (Floorplanner, Figma, Miro):* capped free tiers,
  account-bound, and exports carry nested transforms and clip paths.

Consequences:

- Route overlays cannot misalign: both the map and the `<polyline>` live in the
  same `viewBox`.
- Building data becomes reviewable as a drawing rather than as code, and a plan
  change is an SVG edit plus a compiler run.
- Correctness depends on an authoring contract (no transforms on routing groups,
  chrome separated from geometry, no metadata blobs), enforced by a validator
  that fails the build on violation.
- Human verification against the official plans is a mandatory quality gate,
  since supervised AI vectorization can infer geometry it cannot read.
