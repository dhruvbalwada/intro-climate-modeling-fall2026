# Course website (Quarto)

Public course site — the Quarto successor of the `earth-DS-ML/summer_2026` Jupyter Book workflow. **Only student-facing content lives here**; primers, outlines, solutions, and answer keys stay in `../course_materials/` and must never be copied in.

## Preview locally
```bash
brew install --cask quarto     # once
cd website
quarto preview                 # live-reloading site incl. the slide decks
```

## Publish (replaces ghp-import)

**Live site: https://dhruvbalwada.github.io/intro-climate-modeling-fall2026/**
**Repo: github.com/dhruvbalwada/intro-climate-modeling-fall2026** (this folder is its clone)

After each edit:
```bash
git add -A && git commit -m "..." && git push     # source
quarto publish gh-pages --no-prompt               # deploy (~1 min to go live)
```
Optional later: add Quarto's standard GitHub Action so pushing alone deploys.

## Conventions
- Slides: `slides/weekNN.qmd` (revealjs front matter in each file; they render as pages of this site — link them from `schedule.qmd`).
- Lab handouts: `labs/labN.qmd`. Canonical source for Lab 0 text is `../course_materials/labs/lab0_setup/LAB0_instructions.md` — if you edit one, mirror the other (or edit the qmd and back-port).
- Placeholders to fill before publishing: `[ROOM]`, `[TA ...]`, `[DAYS/TIMES]`, `[HUB-URL]`, `[INSTRUCTOR-GITHUB]`, `[TA-GITHUB]`, `GITHUB-ORG/GITHUB-REPO`.
