# Gameboard MVP Spec (Draft)

Date: 2026-02-13  
Status: Draft for review before implementation

## 1. Purpose
Define a first implementation of a 2D creature simulation that includes:
- a gameboard with vector `x, y` coordinates,
- sprite-based creature rendering,
- a control panel for GUI inputs,
- a status/statistics panel,
- extensible rules for simulation behavior,
- headless automated tests,
- a graphics smoke test,
- config defaults plus CLI flags,
- screenshot capture with optional description in filename.

## 2. Out of Scope (for MVP)
- Complex creature AI, genetics, or evolution algorithms.
- Performance optimization beyond basic responsiveness.
- Networking, save/load systems, or replay system.
- Advanced UI theming.

## 3. Functional Requirements

### 3.1 World and Coordinates
- The simulation world is a 2D board using vector coordinates (`x: float`, `y: float`).
- Board dimensions are configurable.
- Coordinate system origin and axis direction must be documented in code comments or docs.
- Creatures have position and velocity vectors.

### 3.2 Creatures and Rendering
- Creatures are rendered as sprites in the gameboard panel.
- Rendering scale and sprite size are configurable.
- Display layer should be separate from simulation update logic so headless tests can run without pygame.

### 3.3 Panels and GUI Layout
- Main window has three visible areas:
  - Gameboard panel (primary simulation view)
  - Controls panel (buttons/inputs)
  - Status/statistics panel (readouts)
- Minimum controls:
  - `Play/Pause`
  - `Step` (single tick)
  - `Reset`
  - `Screenshot` button
  - Text input for optional screenshot description
- Minimum status fields:
  - Tick count
  - Creature count
  - Simulation state (`running` or `paused`)

### 3.4 Extensible Rules
- Rules for movement, interactions, and display behavior must be extensible.
- MVP architecture should support adding new rules without rewriting core loop.
- Suggested approach:
  - Simulation step calls a list of rule objects/functions.
  - Interaction rules operate on simulation state, not rendering code.
  - Display mapping (state -> sprite/frame/color) is configurable/replaceable.

### 3.5 Configuration and CLI
- Provide a config file with default parameters.
- Provide CLI flags that override config defaults.
- Required configurable parameters (minimum):
  - board width/height
  - initial creature count
  - tick rate or step duration
  - random seed
  - sprite size
  - screenshot output directory
- CLI should support `--headless` mode.

### 3.6 Screenshot Capture
- `Screenshot` control captures current GUI frame to disk.
- Optional description text input is appended in filename.
- Filename must include a timestamp and sanitized description.
- Example filename format:
  - `2026-02-13_154210-first_movement_rule.png`
  - `2026-02-13_154210.png` (no description)

## 4. Non-Functional Requirements
- Python project managed with `uv` and `pyproject.toml`.
- GUI uses `pygame-ce`.
- Testing uses `pytest`.
- Deterministic behavior available via seed.
- Beginner-readable code: small functions, clear naming, minimal indirection.

## 5. Testing Requirements

### 5.1 Headless Automated Tests
- Tests must run without opening GUI windows.
- Minimum test set:
  - Coordinate update test (position changes from velocity).
  - Boundary behavior test (e.g., clamp, wrap, or bounce per selected rule).
  - Interaction rule test (basic creature-creature or creature-world interaction).
  - Config + CLI override precedence test.
  - Screenshot filename sanitization unit test.

### 5.2 Graphics Smoke Test
- Provide a smoke test command/script that:
  - starts GUI,
  - renders at least one frame with one creature sprite,
  - exits cleanly after a short duration or one frame.
- Smoke test result is reported in session notes (pass/fail).

## 6. Proposed Initial Package Layout

```text
src/evosim/
  config.py
  cli.py
  math2d.py
  model.py
  rules.py
  simulation.py
  render.py
  ui.py
  screenshot.py
  app.py
tests/
  test_simulation.py
  test_rules.py
  test_config_cli.py
  test_screenshot.py
scripts/
  smoke_graphics.py
```

## 7. Acceptance Criteria (MVP)
- Running CLI in GUI mode shows gameboard + controls panel + status panel.
- At least one creature sprite is visible and updates over ticks.
- `Play/Pause`, `Step`, `Reset`, and `Screenshot` controls work.
- Screenshot filenames include timestamp and optional description.
- Config defaults load successfully; CLI flags override correctly.
- Headless pytest suite passes.
- Graphics smoke test passes on developer machine.

## 8. Open Decisions to Confirm Before Coding
- Boundary rule for MVP: `wrap`, `bounce`, or `clamp`?
- Interaction MVP: collision count only, or simple state change?
- Control panel implementation style in pygame-ce: custom widgets vs minimal manual hitboxes?
- Preferred config format: `toml`, `yaml`, or `json`?
- Target FPS/tick defaults for first lesson.

## 9. AGENTS.md Relationship
- `AGENTS.md` should remain process/policy guidance for sessions and collaboration.
- This requirements doc is product/feature scope and acceptance criteria.
- Keep them separate to avoid mixing workflow policy with implementation requirements.
