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
│   └── devlog.md
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
