from sim.pygame_view import (
    BUTTON_TOP_GAP,
    PANEL_STATUS_TOP,
    STATUS_LINE_HEIGHT,
    apply_button_action,
    build_buttons,
    build_status_lines,
    click_repeats,
    screenshot_path,
)
from sim.simulation import Simulation, SimulationConfig
import pygame


def test_build_buttons_creates_numerous_controls() -> None:
    buttons = build_buttons(world_width_px=600, top=248)
    labels = [button.label for button in buttons]
    assert labels == [
        "Play",
        "Pause",
        "Step",
        "Reset",
        "More Creatures",
        "Fewer Creatures",
        "More Food",
        "Less Food",
        "Faster",
        "Slower",
        "Screenshot",
        "Quit",
    ]


def test_build_status_lines_includes_creature_count() -> None:
    sim = Simulation(SimulationConfig(creatures=8, seed=7))

    status = build_status_lines(sim, playing=True, fps=60)

    assert "Creature Count: 8" in status
    assert "Food Count: 250" in status
    assert "Largest Creature: 1.00" in status


def test_buttons_can_be_positioned_below_stats() -> None:
    sim = Simulation(SimulationConfig(creatures=8, seed=7))

    status = build_status_lines(sim, playing=True, fps=60)
    top = PANEL_STATUS_TOP + len(status) * STATUS_LINE_HEIGHT + BUTTON_TOP_GAP
    buttons = build_buttons(world_width_px=600, top=top)

    assert buttons[0].rect.top == top
    assert buttons[0].rect.top > PANEL_STATUS_TOP + (len(status) - 1) * STATUS_LINE_HEIGHT


def test_click_repeats_uses_ctrl_and_shift_modifiers() -> None:
    assert click_repeats(0) == 1
    assert click_repeats(pygame.KMOD_CTRL) == 10
    assert click_repeats(pygame.KMOD_SHIFT) == 100


def test_apply_button_action_ctrl_adds_ten_creatures() -> None:
    sim = Simulation(SimulationConfig(creatures=8, food=0, seed=7))

    sim, _, _, _, _, _ = apply_button_action(
        clicked="More Creatures",
        sim=sim,
        config=sim.config,
        current_fps=60,
        playing=True,
        screenshot_dir="screenshots",
        screen=None,
        mods=pygame.KMOD_CTRL,
    )

    assert len(sim.creatures) == 18


def test_apply_button_action_shift_adds_one_hundred_food() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7))

    sim, _, _, _, _, _ = apply_button_action(
        clicked="More Food",
        sim=sim,
        config=sim.config,
        current_fps=60,
        playing=True,
        screenshot_dir="screenshots",
        screen=None,
        mods=pygame.KMOD_SHIFT,
    )

    assert len(sim.food) == 100


def test_screenshot_path_uses_png_in_directory() -> None:
    path = screenshot_path("screenshots")
    assert path.parent.name == "screenshots"
    assert path.suffix == ".png"
