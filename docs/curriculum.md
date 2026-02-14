# Living Curriculum

Purpose: This is the project learning roadmap and pacing document.
Use it as the single source of truth across sessions.

Last updated: 2026-02-14

## Program Goals
- Teach Judah core Python and simulation thinking through playful experiments.
- Build a 2D creature world where interactions evolve over time.
- Keep progress visible for reflection and school-credit records.

## Current Focus
- Phase: Foundations
- Current target: First gameboard MVP with vector coordinates, creature sprites, controls panel, and status panel.
- Current session update (2026-02-13): Defined standards workflow, evidence policy, and drafted MVP spec.
- Definition of done for this phase:
  - Headless simulation step works and is tested.
  - GUI shows gameboard, controls, and status/stats panel.
  - Screenshot capture includes timestamp and optional description.

## Next Session Draft
- Primary goal: Scaffold initial project code structure and run first passing headless tests.
- Stretch goal: Add minimal GUI smoke test and one visible sprite.
- Student challenge: Explain the separation between simulation logic and rendering.
- Next-session task list:
  - Start by reviewing `docs/specs/gameboard-mvp.md` together and confirming the first implementation slice.
  - Set up `src/` and `tests/` for simulation core.
  - Implement vector position update for creatures.
  - Add one boundary rule and tests.
  - Add minimal pygame window with gameboard + side panels.

## Backlog
### Ready Now
- Build deterministic creature movement step.
- Add tick counter and creature count stats.
- Add config defaults and CLI override wiring.

### Next
- Add interaction rules plugin structure.
- Add pause/step/reset controls.
- Add screenshot button and description field.

### Later
- Add richer behaviors and experiment presets.
- Add automated multi-run headless experiments.
- Add comparative result summaries.

## Completed Milestones
| Date | Milestone | Notes |
|---|---|---|
| 2026-02-13 | Planning and standards baseline established | Shared standards repo, synced workflow, MVP spec draft, session documentation structure. |

For update procedure, see:
- `shared/sheffler_standards/docs/playbooks/session-management.md`
