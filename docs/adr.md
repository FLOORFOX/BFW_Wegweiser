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

**Status:** Accepted

**Context:** While usage insights (popular destinations, points where users get
confused) will help improve signage and instructions, routing is strictly a
read-only static delivery path. Analytics is fundamentally a write path
(client → collector) that cannot reuse static JSON distribution.

**Decision:** Defer analytics infrastructure during early development. When
implemented, keep analytics completely decoupled from routing:
- Kiosk phase: local, append-only log files with zero external infrastructure.
- Mobile/hosted phase: a minimal event-collection endpoint or a third-party
  privacy-focused service.
- Privacy by design: never collect or store data traceable to individual users;
  formalize a clear privacy policy before activating any data collection.

**Consequences:**
- No premature infrastructure or telemetry code built during prototype stages.
- Routing remains completely static, self-contained, and performant regardless of
  analytics decisions.
- Privacy and compliance constraints are established deliberately upfront rather
  than retrofitted.
