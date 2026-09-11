# Wegweiser — Axioms

The conceptual space the algorithm lives in, and the rules it functions within.

---

## Objects

**1.** A **zone** is a space. A **portal** is a boundary between two zones. Nothing else exists.

**2.** Every portal joins **exactly two** zones. No exceptions.

**3.** A zone has **at least one** portal.

---

## The defining constraint

**4.** Within a zone, every portal is directly reachable from every other. *If not, it isn't one zone — split it.*

---

## Derived, never authored

**5.** Zone → portals is the inverse of the portal record.

**6.** Segments are all portal pairs within a zone.

**7.** A **state** is written `zone_from | portal | zone_to`. Each portal yields exactly two, one per direction. The order carries the direction; both zones are named explicitly, so a state is self-standing.

---

## Movement

**8.** All travel is portal to portal within one zone. Every zone on a route is crossed — entered by one portal, left by another. The start zone is only left; the target zone is only entered.

**9.** From a state, the successors are every other portal of the zone just entered, each written as a new state entering its own far zone.

**10.** **Distance** belongs to the unordered portal pair within a zone — symmetric, measured from the Grundriss. **Special costs** are assigned by the designer to individual states.

---

## Queries

**11.** Start and target are zones, not portals.

**12.** Start states are the **outbound** states of the start zone; target states are the **inbound** states of the target zone. The search runs from the start set to the target set. Multiple portals need no special handling in either role.

---

## Structure

**13.** A **segment** is a traversal of one zone between two of its portals. As two consecutive states it yields the zone, the direction from the order, and the distance from the unordered pair. A **route** is a chain of segments.

---

## Canonical form

**14.** A route is written as one strictly alternating sequence beginning and ending with a zone:

```text
zone₁ portal₁ zone₂ portal₂ zone₃ … portalₙ zoneₙ₊₁
```

This is the complete representation. States and segments are two interleaved sliding windows over it, each advancing by one portal:

| Read | Window | Anchored on |
| --- | --- | --- |
| **state** | `zone portal zone` | zones |
| **segment** | `portal zone portal` | portals |

Consecutive segments overlap by one state; every state but the first and last both ends one segment and begins the next.

Everything derives from this single sequence — direction from the left-to-right order, distance from each segment's unordered portal pair within its zone, special costs from each state, and the instruction text from the zone names in order.

For a route of *n* portals: *n* states, *n* − 1 segments, *n* + 1 zones. The first zone is only left and the last only entered, per axiom 8.

**Validity check:** for every `zoneA portal zoneB` triple, that portal's two zones must be exactly {zoneA, zoneB}. A sequence failing this is malformed.

**15.** A route takes one of three shapes, by the relation between start and target zone:

| Case | Shape | Condition |
| --- | --- | --- |
| 1 | one access segment | start and target are the same zone |
| 2 | two access segments | start and target zones share a portal |
| 3 | two access segments + *n* transit segments | otherwise |

Not a collapse of the general case but a reduction of it: the transit portion shrinks to zero, the access portions never do.

---

## Movement geometry

**16.** A **movement zone** is the walkable part of a zone — obstacles excluded. It lies **wholly within one zone**. A stripe of circulation space spanning a boundary is two movement zones meeting at the portal, never one crossing it.

**17.** Movement lines are derived by **convex decomposition** of the movement zone. The resulting virtual portals are the vertices of the polyline. Human designers may override the derived line where real movement patterns deviate from geometric optima.

**18.** **Access segments** — the first and last segment of a route — are direct lines from the terminus portal to the preceding portal, or in a complex zone to the last virtual portal of the relevant convex cell. They do not follow the movement line.

**Transit segments** follow it: a virtual portal lies on the line and is located by its position along it; an off-line portal additionally needs a foot point and a stub.

**19.** A portal's role — **initial**, **transit**, or **terminal** — is a property of the route, assigned per query. No static classification is possible: a two-door room is a terminus for routes that end there and a transit zone for routes that pass through it.
