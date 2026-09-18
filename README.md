# BFW Wegweiser

Indoor navigation system prototype designed to assist routing within the BFW facility.

## Homepage

- [Open East Wing Viewer](https://floorfox.github.io/BFW_Wegweiser/web/east_wing.html)

## Architecture

The repository adopts a two-tier architecture separating data preparation from presentation:

- [src/](src/): Python graph compiler defining coordinates, weights, and precomputing route data.
- [web/](web/): Static client displaying the floor plan and rendering route overlays in the browser.

## Requirements

- **Python 3.12+** (standard library only; no external packages required)
- **Modern web browser** (Chrome, Edge, Firefox, Safari)

## Quick Start

1. **Compile routing data**:

   ```powershell
   python src/main.py
   ```

   *(Generates `web/data.json` and `web/data.js`)*

2. **Open the viewer**:
   Open `web/index.html` directly in your browser, or serve it locally:

   ```powershell
   python -m http.server -d web 8000
   ```

3. **Run tests**:

   ```powershell
   python -m unittest discover -s src
   ```

## East-Wing Prototype

The east-wing prototype follows the model in
[docs/rulebook_sorted.md](docs/rulebook_sorted.md) and remains separate from the
existing kiosk. Build its source database and precompute all ordered
zone-to-zone routes:

```powershell
python src/build_database.py
python src/calculate_routes.py
```

This writes `database.json` and `database_with_routes.json` at the repository
root. Serve the repository root so the browser can load the routed database and
the semantic floor-plan SVG:

```powershell
python -m http.server 8765
```

Open `http://localhost:8765/web/east_wing.html`.

## Workspace Layout

```text
wegweiser/
├── .gitignore
├── README.md
├── database.json
├── database_with_routes.json
├── docs/
│   ├── adr.md
│   ├── axioms.md
│   ├── convergences.md
│   ├── design_recap.md
│   ├── devlog.md
│   ├── glossary.md
│   ├── graphic_strategy.md
│   ├── rulebook_sorted.md
│   └── roadmap.md
├── src/
│   ├── build_database.py
│   ├── calculate_routes.py
│   ├── main.py
│   └── test_main.py
└── web/
    ├── assets/
   │   ├── bfw-eg-ost.svg
    │   └── Grundriss_mit_Knotenpunkten.png
    ├── data.js
    ├── data.json
   ├── east_wing.css
   ├── east_wing.html
   ├── east_wing.js
    ├── index.html
    ├── script.js
    └── style.css
```

## Conceptual Model

Routing operates on a dual graph: **portals** are nodes, **zone** crossings are
edges. A zone is a space, a portal is a boundary between exactly two zones, and
nothing else exists. The model is fixed by [docs/axioms.md](docs/axioms.md) and
[docs/glossary.md](docs/glossary.md); floor plans are authored as semantic SVG
per [docs/graphic_strategy.md](docs/graphic_strategy.md).

## Roadmap

- [x] Two-tier architecture (offline Python compiler & static web visualizer)
- [ ] Phase 1: Floor plan preprocessing & asset contract
- [ ] Phase 2: Topology extraction & compiler decoupling
- [ ] Phase 3: Algorithm selection & routing engine
- [ ] Phase 4: Cost model & movement geometry
- [ ] Phase 5: Facility-wide coverage & destination partitioning (~200–300 zones)
- [ ] Phase 6: Multi-floor movement & accessibility
- [ ] Phase 7: Precomputation & human guidance

Phases map 1:1 to GitHub Milestones (macro view); technical bullet points in [docs/roadmap.md](docs/roadmap.md) map to actionable GitHub Issues (micro view).

## Development Workflow

Trunk-based workflow on `main` with linear history:

- **Routine changes**: Pull latest `main`, verify tests pass, commit and push directly.
- **Multi-commit / breaking refactors**: Work on a short-lived branch, rebase, and fast-forward merge:

  ```powershell
  git switch -c feature/name
  # ... work & commit ...
  git fetch origin; git rebase origin/main
  git switch main; git merge --ff-only feature/name
  git push origin main; git branch -d feature/name
  ```

- **Task tracking**: Macro phases map to GitHub Milestones; technical bullet points in [docs/roadmap.md](docs/roadmap.md) map to GitHub Issues.
- **Rule**: Code on `main` must pass all tests at all times (`python -m unittest discover -s src`).
