---
ticket: "N/A"
title: "Repo-Focused GitHub Profile README Redesign"
date: "2026-06-24"
source: "design"
---

# Repo-Focused GitHub Profile README Redesign

## Goal

Redesign `natejswenson/natejswenson` (the GitHub profile README) to center on a
curated set of public repositories, replacing the prior near-empty README
(typing GIF + two social badges) and superseding the aspirational, never-shipped
`README-SPEC.md` (AWS/skills/certs/stats brief).

## Identity surfaced by research

Across 10 public non-fork repos, a clear theme emerged: **agent-first / Claude
Code tooling, local-first self-hosted apps, and CLIs**. The redesign leans into
that identity rather than the older "Cloud/AWS/DevOps" framing in the stale spec.

## Decisions

| Dimension | Decision | Rationale |
|---|---|---|
| Featured repos | `local-fitness-dude`, `traefik-local-cli`, `claude-skills`, `llm-token-calculator` (in that order) | User hand-picked the four flagship, CI-backed, agent-themed projects. |
| Card style | Curated 2×2 cards (HTML `<table>`), hand-written pitch + tech chips, **no star counts** | All repos have 0 stars; live pin cards would render ⭐0 and undersell the work. Curated copy controls the narrative; inline-code chips avoid a third-party dependency. |
| Supporting sections | Typing GIF header + Connect footer only | User chose a lean, repo-focused page; declined the tech-stack strip and GitHub stats widgets. |
| GIF text | Regenerated with typos fixed: "Contious"→"Continuous", "experieced"→"experienced" | Visible errors in the visual signature. |
| GIF font | Added macOS Menlo/Courier `.ttc` paths to `generate_readme_gif.py` | Prior macOS path (`Courier.dfont`) did not exist; fell back to ugly bitmap font. |
| GIF image path | GitHub raw URL (`raw.githubusercontent.com/.../main/output.gif`) | Canonical remote is GitHub; keeps regenerated GIF and README in one repo. Replaces the prior deliberate GitLab URL. |
| Tests | `readme.test.js` rewritten to validate the new structure | Old suite asserted the unshipped spec (and "must NOT have Featured Projects"), directly conflicting with this design; it was already fully failing. |

## Final structure

```
1. Typing GIF header   (regenerated; Menlo font; typos fixed; GitHub raw URL)
2. ## 🚀 Featured Projects   (2×2 HTML-table cards — the centerpiece)
3. Connect footer      (CTA line + LinkedIn · Website badges, centered)
```

### Card copy

| Repo | Pitch | Tech chips |
|---|---|---|
| 🏋️ local-fitness-dude | Agent-first fitness coach — Garmin → local SQLite, deterministic training-load math (CTL/ATL/TSB) exposed to Claude over MCP. | Python · MCP · SQLite · Flask |
| 🔀 traefik-local-cli | Onboard any local app to a hardened Traefik proxy at `<app>.internal` via a bundled Claude Code skill with hard pass/fail gates. | Bash · Claude Code · Docker |
| 🧩 claude-skills | Monorepo of independently-released Claude Code skills (devlog, ghostwriter, resume, github-stats); namespaced releases, path-filtered CI. | JavaScript · Python · Bash |
| 🔢 llm-token-calculator | Token-counting web app across OpenAI & Anthropic models; Flask backend, security-hardened, WCAG 2.1 AA, dark mode. | Python · Flask · JavaScript |

## Invariants

**Checkable by inspection (enforced by `readme.test.js`):**
- GIF embedded via the GitHub raw URL; no `gitlab.com` reference.
- GIF alt text names "Nate Swenson".
- A `## Featured Projects` heading exists.
- Exactly four repo cards, each linking `https://github.com/natejswenson/<repo>`.
- Tech chips present (`MCP`, `Claude Code`, `Flask`, `Docker`).
- Connect footer links LinkedIn + `natejswenson.com` and includes a CTA.
- No `github-readme-stats` / `streak-stats` third-party widgets.

**Testable / manual:**
- GIF renders with the Menlo font and brand-colored shapes (red/yellow/teal/blue) — verified via exported final frame.
- Cards render as a two-column grid on GitHub's renderer.

## Out of scope (YAGNI)

- GitHub stats / streak / top-language widgets.
- Tech-stack badge strip.
- About / certifications / volunteer / languages sections from the old spec.
- Repos beyond the curated four (github-stats-cli is represented via `claude-skills`).

## Follow-ups

- `README-SPEC.md` is now stale; this design doc is the source of truth. Leaving
  it in place (harmless) — delete in a later pass if desired.
- If the README is ever mirrored to GitLab again, swap the GIF URL back and push
  the regenerated `output.gif` there too.
