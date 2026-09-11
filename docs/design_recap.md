# Wegweiser — Design session recap

Record of a design conversation, September 2026. What was decided, what was
discarded, and where the project stood at the end.

Companion documents: [docs/axioms.md](axioms.md), [docs/glossary.md](glossary.md),
[docs/convergences.md](convergences.md), `validate_plan.py`.

---

## 1. Starting point

The opening proposal: break routing into three stretches — reach a known hub,
cross a precomputed hub-to-hub middle, invert the first stretch for the last
leg. Users are assumed to know where they are and where they want to go.

This maps to **HPA\*** and **transit node routing**. Two concerns raised at the
outset, both of which turned out to be central:

- Nearest-hub-first can miss shorter routes that bypass the nearest hub.
- Recovery after a wrong turn needs named landmarks the user can report.

---

## 2. The reframing

Several turns in, the model was restated in a way that changed the project:

> *"For traversing each zone, the start and end points get updated, leading to
> segments that form a chain."*

This is not places linked by corridors. It is **portals linked by
zone-crossings** — the dual graph, formalised in indoor navigation as the
IndoorGML node-relation graph.

The inherited code was the conventional model; the intended design had been the
dual all along. Consequences:

- Cost lives on the traversal, so turn penalties need no special machinery.
- Arrival direction is expressible, which the conventional model cannot do.
- Rooms are never crossed; start and target are the only zones not traversed.

---

## 3. What was derived

Formalisation proceeded by correction rather than addition. The load-bearing
results, in the order they settled:

**Arity-2.** A portal joins exactly two zones, without exception. This makes
zone→portals a pure inversion of the portal record, makes the segment list
derivable rather than authored, and reduces direction tracking to picking the
other element of a pair. It is also what keeps the duality clean in both
directions — a portal joining three zones would require a hypergraph.

**Axiom 4 as the boundary test.** *If two portals in a space are not directly
reachable from each other, it is not one zone — split it.* This is not an
observation about buildings but the definition of a zone, and it gives a working
rule for data entry that needs no categories.

**The state.** `zone_from | portal | zone_to`. Direction carried by the order,
both zones named so the state stands alone. Each portal yields exactly two. The
algorithm is Dijkstra over states; search space is 2 × portal count.

**The canonical form.** A route is one strictly alternating sequence beginning
and ending with a zone. States and segments are two interleaved sliding windows
over it. Everything — direction, distance, special costs, instruction text —
derives from this single sequence.

**Movement geometry as a separate layer.** Movement zones are the walkable part
of a zone, obstacles excluded, contained wholly within one zone. Movement lines
are derived by convex decomposition; the resulting vertices are the polyline
vertices. Access segments are direct lines and do not follow the movement line;
transit segments do.

**Roles are per-query.** Initial, transit and terminal are properties of the
route, not of the portal. No static classification is possible, since a two-door
room is a terminus for some routes and a transit zone for others.

Result: **19 axioms**.

---

## 4. What was discarded

| Discarded | Why |
| --- | --- |
| Hub, junction, Knotenpunkt as distinct terms | All the same object as a portal |
| "Decision point" | Every portal is a transition; only some offer a choice |
| Crossable / terminal zone classification | Invented category, not stored, not needed |
| Branch / leaf as derivable from portal count | A room with three doors defeats any count-based rule |
| `connections` as a code term | Renamed to `edges` for literature compatibility |
| Non-room partitions as zones | Booths, counters and cubicles are obstacles |
| `wegweiser-design.md` | Written before the reframing; superseded by the axioms |

---

## 5. Algorithm evaluation

At this scale every candidate runs in well under a millisecond, so speed is not
a criterion. What discriminates: correctness under loops, instruction quality,
deviation robustness, authoring cost, and the asymmetry between ~300
destinations and ~20 decision points.

**Shortlist:**

- **Dijkstra over states** as the engine and ground truth. Unglamorous, always
  correct, handles the cost model.
- **Graph Voronoi + arc flags** as the layer above, because they produce
  something printable and inspectable and match the building's star shape.
- **Yen's k-shortest paths** later, for step-free and accessibility variants.

**Rejected for this building:** A\* (straight-line heuristic is actively bad in a
star topology), D\* Lite (recomputing is cheaper than repairing at this scale),
contraction hierarchies and hub labelling (continental-scale machinery).

**Kept as reference:** BFS, as the original implementation and an algorithmic
regression baseline.

One observation that shaped the shortlist: **route choice is rare in this
building.** The star topology means most of the graph has exactly one sensible
path. Any algorithm competing on pathfinding quality competes over a small prize;
the real difficulty is turning a node sequence into usable German instructions.

---

## 6. Repository findings

Reviewed at commit state of 2026-09-10.

**The graph is a tree.** 13 labels, 12 edges, connected, acyclic. Every algorithm
discussed returns identical output on it, so the current dataset cannot
demonstrate any difference between them. Adding the eastern loop is the
highest-value change to the data.

**The premise is not yet in the code.** Checkpoints are corridor positions, not
rooms. There is no room-to-corridor mapping, and the start point is hardcoded to
the Haupteingang. Neither "where I am" nor "where I want to go" is expressible.

**Direction-independent issues:** `start_point` orphaned from the `"startpunkt"`
label after the German→English rename; all coordinates unused; `plt.show()`
blocking before pathfinding, with the path never drawn on the map; valid targets
hardcoded in the prompt string; output a raw Python list.

---

## 7. Floor plan work

Source hierarchy established:

- **Lageplan EG v1.2 (2018)** — geometry, room numbers, wing layout.
- **Flucht- und Rettungsplan B 7967_059 (07.05.2026)** — door positions at
  usable fidelity, current room use. Supersedes the Lageplan where they
  disagree: room numbering has drifted, and the personal names on the 2018 plan
  are eight years stale.
- The Rettungswege drawn on those plans are professionally-drawn movement lines.

A schematic SVG of the east block was produced, then redrawn in Claude Design to
the same markup contract: `<g id="zones">` with `data-kind` and `data-label`,
`<g id="portals">` with `data-a` and `data-b`. The contract makes the portal
record a one-pass parse of the drawing.

**Corrections that landed across iterations:**

- WC vestibules modelled as separate zones — you pass through a Vorraum to reach
  a WC.
- The wing boundary made explicit as an `anschluss` zone.
- Doorless portals drawn as dashed boundaries, derived from axiom 4 without being
  named.
- Architectural door notation clarified: a line plus a quarter-circle arc. Solid
  black blocks are wall thickness, not doors. This fixed the doubled portals.
- Adjacent double doors merged into one portal.
- Non-room partitions demoted from zones to obstacles.

**Open at end of session:** `E.56c` non-convex (0.855); `TR9` with a single
portal, implausible for a Treppenhaus on an escape plan; E.52/Wachdienst overlap
pending the obstacle conversion.

---

## 8. Build order

1. Portal record with coordinates; zone index and segment list derived from it
2. Plain Dijkstra over states — ground truth for testing
3. Convex decomposition; movement lines and obstacles
4. Backward Dijkstra pass → tags, arc flags, next-portal tables
5. Decision loop, with full-route printing as the presentation layer
6. Deviation handling by portal-name localisation
7. Multi-floor, using the per-floor Rettungsplan boards
8. Remaining algorithms as study material on a working system

---

## 9. Open questions

1. **Tag granularity.** One entry per room is precise but produces signs listing
   hundreds of destinations. Grouping makes signage readable and accepts
   suboptimality deliberately. This tradeoff is the real design work.
2. **Portal identification by the user.** How someone states where they are.
   This is every interaction's entry point, not only a recovery path.
3. **Instruction chunking.** How many segments collapse into one printed
   instruction, and which landmarks to name.
4. **Destination vocabulary.** Rooms carry both stable numbers (`E.67`) and
   semantic names (`Tagungsraum`, `Speisesaal`). Users will mix them.
5. **Start position within a zone.** Axiom 11 makes the start a zone, so every
   start state begins at zero cost. Correct in a small room, wrong in the
   Speisesaal. A known and currently accepted imprecision.
