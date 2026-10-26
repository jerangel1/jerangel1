# Profile sources

Everything under `assets/` is generated from the files in this folder, in English (`name.svg`) and Spanish
(`name.es.svg`). `README.md` is the English profile and `README.es.md` the Spanish one; the EN | ES switch at the
top of each links to the other.

| Asset | Source | Rebuild |
|---|---|---|
| `assets/hero*`, `principles*`, `connect-linkedin*`, `chapter-off-the-clock*`, `language-*` | `hero.py` + `fonts/` | `python3 hero.py fonts ../assets` |
| `assets/engineering-ecosystem*.svg` | `ecosystem.py` + `fonts/` | `python3 ecosystem.py fonts ../assets` |

Both scripts share `bounce.py`, the request ball that hops between layers, squashes on landing and leaves an impact ring.

## Engineering ecosystem

Edit `LAYERS` and `COPY` in `ecosystem.py` and run it. It writes four files per language:

- `engineering-ecosystem.svg`: animated, desktop layout.
- `engineering-ecosystem-static.svg`: same layout, no motion (served to `prefers-reduced-motion`).
- `engineering-ecosystem-mobile.svg` and `-mobile-static.svg`: single-column layout for screens up to 600px.

The SVGs follow GitHub's image rules: no scripts, no external requests, animation in SMIL only, and fonts
embedded as WOFF2 data URIs (Archivo and IBM Plex Mono, Latin subset, SIL Open Font License).

## Hero and principles

`hero.py` writes the hero (animated, static, mobile and mobile static) and the principles cards (desktop and
mobile), the LinkedIn button, the closing band and the language switch. Edit `COPY` at the top and run it.

## Publish

```bash
git add README.md README.es.md assets src
git commit -m "feat: redesign profile README"
git push
```

GitHub caches images through its proxy. If a change does not show up, wait a few minutes or change the file name.
