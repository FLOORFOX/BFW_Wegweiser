# BFW Wegweiser

Indoor navigation system prototype designed to assist routing within the BFW facility.

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

## Workspace Layout

```text
wegweiser/
├── .gitignore
├── README.md
├── docs/
│   ├── adr.md
│   ├── devlog.md
│   └── roadmap.md
├── src/
│   ├── main.py
│   └── test_main.py
└── web/
    ├── assets/
    │   └── Grundriss_mit_Knotenpunkten.png
    ├── data.js
    ├── data.json
    ├── index.html
    ├── script.js
    └── style.css
```

## Roadmap

- [x] Two-tier architecture (offline Python compiler & static web visualizer)
- [ ] Phase 1: Dijkstra baseline with Euclidean pixel distance weighting
- [ ] Phase 2: Walking cost penalties (turns, doors) & multi-floor transitions
- [ ] Phase 3: Facility-wide graph expansion (~200–300 rooms)
- [ ] Phase 4: Precomputed next-hop decision tables & human instruction generation

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
