# Wegweiser — Glossary

Fixed terminology. Where a word was rejected, the reason is given, because the
rejected ones are the ones that creep back.

---

## Core objects

**Zone** — a space. Every point of the building belongs to exactly one zone.
Defined by axiom 4: all its portals must be reachable from every other by an
unhindered path. If they are not, it is not one zone.

**Portal** — a boundary between two zones. Joins **exactly two**, no exceptions.
A portal need not be a door: a doorless opening, or a line drawn across a
corridor at a corner, is equally a portal.

**Virtual portal** — a portal with no physical door, created by splitting a zone
to satisfy axiom 4. Same object as any other portal; the adjective is for the
human drawing the plan, not for the algorithm.

**Obstacle** — a fixed thing inside a zone that is not walkable and that nobody
routes to or through: a counter, a booth, seating, an atrium void. Excluded from
the movement zone. **Not a zone**, even when it has walls and a door.

> **Test:** a zone is either a destination someone would ask for, or a space
> traversed to reach something else. Anything that is neither is an obstacle.

---

## Derived objects

**State** — written `zone_from | portal | zone_to`. The direction is carried by
the order; both zones are named, so a state stands alone without lookup. Each
portal yields exactly two states.

**Segment** — a traversal of one zone between two of its portals. Written
`portal zone portal`. As two consecutive states it yields the zone, the
direction from the order, and the distance from the unordered portal pair.

**Route** — a chain of segments, written in the canonical form:

```text
zone₁ portal₁ zone₂ portal₂ zone₃ … portalₙ zoneₙ₊₁
```

Strictly alternating, beginning and ending with a zone. States and segments are
two sliding windows over it.

**Zone index** — zone → its portals. Derived by inverting the portal record,
never authored.

---

## Movement geometry

**Movement zone** — the walkable part of a zone, obstacles excluded. Lies
**wholly within one zone**; never spans a portal. Circulation space crossing a
boundary is two movement zones meeting at the shared portal.

**Movement line** — the path people actually walk through a movement zone.
Derived by convex decomposition; the resulting vertices are the polyline
vertices. Hand-adjustable where real behaviour departs from geometric optima.

**Foot point** — a portal's position along a movement line.
**Stub** — the short hop from a portal to its foot point. Both apply only to
transit through an off-line portal; virtual portals lie on the line, and access
segments are direct lines that need neither.

---

## Route roles

Assigned **per query**, never statically. The same door is a terminus for routes
that end there and a transit portal for routes passing through.

| Role | Meaning |
| --- | --- |
| **initial** | the portal leaving the start zone |
| **transit** | any portal crossed on the way |
| **terminal** | the portal entering the target zone |

**Access segment** — the first or last segment of a route. A direct line from the
terminus portal to the preceding portal, or in a complex zone to the last virtual
portal of the relevant convex cell. Does not follow the movement line.

**Transit segment** — any segment between them. Follows the movement line.

**Route cases** — three shapes: (1) one access segment, same zone; (2) two access
segments, adjacent zones; (3) two access segments plus *n* transit segments.

---

## Graph terms

**Node** and **edge** — the mathematical words. Used at the graph layer, because
every paper and library uses them and a local vocabulary costs a translation tax
on every lookup. "Edge" is a fossil from polyhedra and describes nothing here;
keep it anyway.

**`edges`** in code, not `connections` — renamed for the same reason.

**Layer split:**

| Layer | Contents | Used for |
| --- | --- | --- |
| Graph | portals as nodes, segments as edges | routing |
| Index | zones as keys, portals as values | instruction text |

Joined by one field: each segment records the zone it crosses.

---

## Rejected words

| Word | Why |
| --- | --- |
| **Hub** | Same object as a portal, with a busyness connotation the algorithm never reads. |
| **Knotenpunkt / junction** | Same object as a portal. |
| **Decision point** | Wrong: every portal is a transition, only some offer a choice. Two properties, not one. |
| **Crossable / terminal zone** | Invented category, derivable from portal count. Not stored. |
| **Branch / leaf** | A designer's judgement about function, not derivable from topology — a room with three doors defeats any count-based rule. Not used by the algorithm. |
| **Connections** | Replaced by `edges` at the graph layer. |

---

## Naming conventions in data

- Zone ids: room number as printed (`E.54a`, `R.58`) or a lowercase ASCII slug
  (`flur_nord`, `atrium`). Exterior is `aussen`.
- Portal ids: sequential (`p01`, `p02`).
- Labels: German, as on the plan (`Unterricht`, `Besprechungsraum`).
- Identifiers, structure, commit messages and docs in English; comments and
  user-facing strings in German. Node label *values* stay German, since they
  share a namespace with user-typed destination names.

---

## Duplicate portals

Two portals between the same pair of zones are worth keeping separate only if
they are far enough apart that the choice between them changes a route. Adjacent
doors → one portal. Doors at opposite ends of a corridor → two.
