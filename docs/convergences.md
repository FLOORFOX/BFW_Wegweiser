# Wegweiser — Convergences

Concepts derived from first principles during design, and their established names in the literature. For reference and further reading.

---

## Full set

| # | Derived | Established name | Field |
| --- | --- | --- | --- |
| 1 | Three-stretch decomposition: reach a known hub, precomputed hub-to-hub middle, inverse for the last stretch | HPA\* (Botea, Müller, Schaeffer 2004); Transit Node Routing (Bast et al. 2006); multi-level graphs | Game AI; road-network route planning |
| 2 | Nearest-hub-first can miss shorter routes that bypass the nearest hub | Optimality loss under fixed cluster entrances | Hierarchical pathfinding |
| 3 | Subway-exit signage: assign landmarks by real access cost, not birds-eye distance | Graph Voronoi diagram; arc flags (Lauther 2004) | Network analysis; road routing |
| 4 | Direction pruning, repeated at each decision point | Routing tables, distance-vector routing; flow fields / Dijkstra maps | Computer networking; game development |
| 5 | Zones as edges, portals as nodes | Dual graph / line graph; Node-Relation Graph of IndoorGML; Poincaré duality | Graph theory; GIS; OGC indoor standards |
| 6 | "If two portals aren't directly connected, it isn't one zone — split it" | Convex cell decomposition of free space | Robot motion planning |
| 7 | A portal joins exactly two zones; the portal record inverts to the zone index | Bipartite incidence structure; incidence matrix | Combinatorics; topology |
| 8 | State written `zone \| portal \| zone`, direction carried by the order | Edge-based expansion; turn-aware routing | Road routing; state-space search |
| 9 | Canonical alternating zone-portal-zone chain | Portal sequence ("channel", "corridor") | Navmesh pathfinding |
| 10 | Convex cells → virtual portals → polyline through them | Navigation mesh pipeline; funnel algorithm (string-pulling) | Game AI; robotics |
| 11 | Three route cases by zone adjacency (axiom 15) | Locality filter — TNR's fallback to local search for near pairs | Road routing |
| 12 | A portal is where the zone-before differs from the zone-after | Boundary in point-set topology; portal in rendering | Topology; computer graphics (Doom/Quake portal culling) |
| 13 | Prescribed paths people actually walk, not geometric optima | Desire lines; preferred-path networks | Urban planning; architecture |
| 14 | Movement as a series of dimensionless directed instants | Velocity field / flow field; continuous-time trajectory | Physics; control theory |
| 15 | Movement zones and lines; initial/terminal vs transit portals | Core network + access edges; medial axis / skeleton | Transit node routing; computational geometry |

---

## Reading priority

**Navigation mesh construction** is the closest existing pipeline to this design, and covers rows 6, 9 and 10 as one method:

> Decompose free space into convex polygons → shared edges become portals → graph search over polygons yields a portal sequence → the **funnel algorithm** (Lee & Preparata 1984; "Simple Stupid Funnel Algorithm" for a readable modern treatment) pulls a taut shortest path through that sequence.

The funnel step is the one part not yet derived here, and it addresses the same problem as prescribed movement lines: given a chain of portals, what is the actual walked line. Worth reading before hand-drawing movement lines, since it may compute a usable default to override only where human behaviour departs from taut-string geometry.

**IndoorGML** (OGC standard) formalises rows 5 and 7 — cells, boundaries, and the node-relation graph — and has already done the standardisation work for indoor navigation specifically.

**Transit Node Routing** (rows 1, 11, 15) is the closest match for the access/transit split and the locality fallback.
