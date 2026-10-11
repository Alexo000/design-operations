# Design Operations explorer

The public explorer for the Design Operations Compendium: 144 operations, a few questions to find one for your situation, and a map of the whole collection.

## What is where

| Folder | What it holds |
|---|---|
| `site/` | The finished page, `index.html`. This is the only folder that goes online. |
| `build/` | The scripts that make the page. |
| `sources/` | What the scripts read: the Compendium (2 October 2026), the August beta page and its content register, the symbols, and the task-card icons. **Private: not on GitHub.** It lives in the Dropbox copy of this folder; the Compendium's home is the Shubidubi project knowledge. |
| `assets/social/` | Share image and Instagram images. |

## Rebuild the page

You need Python 3. Nothing else for a normal rebuild.

```
python3 build/build_explorer.py
```

This writes `site/index.html` and a check list, `build/build_report.tsv`.

To use a newer Compendium, put it in `sources/` and run:

```
SRC=sources/<new compendium file>.md python3 build/build_explorer.py
```

`build/glyphs.py` only matters if the task-card icons change. It needs the `fonttools` package and the DejaVu Sans font.

## What each script does

- `build_explorer.py`: the main build. Reads the Compendium and refills the beta page with the 144 operations.
- `parse_full.py`: reads Compendium entries.
- `onboarding.py`: the "How it works" screen with five worked examples.
- `seen.py`: the "seen" tally and the map button.
- `nav.py`: Back button, links to single cards, results with reasons, plain wording.
- `symbols_draw_153_155.py`, `symbols_dsl.py`: symbols for the three newest operations.
- `glyphs.py`: the four small icons on the task cards.

## Publishing

The page is published with GitHub Pages at https://operations.ramos-saavedra.com. Every push to `main` publishes `site/` (see `.github/workflows/pages.yml`).

This repository is public and holds only the page, the build scripts and the social images. `sources/` is listed in `.gitignore`, so the Compendium and the other source files are never uploaded. A rebuild needs the Dropbox copy of this folder, where `sources/` sits next to everything else.

The address comes from one DNS record in Squarespace (CNAME `operations` → `alexo000.github.io`) and the custom domain set in the repository's Settings → Pages. If the address changes, change `SITE_URL` in `build/standalone.py` and rebuild.
