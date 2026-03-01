from dataclasses import dataclass
from datetime import datetime
from math import sqrt
from pathlib import Path

import pygame

from sim.simulation import Simulation, SimulationConfig


BACKGROUND = (245, 244, 238)
PANEL_BACKGROUND = (230, 227, 220)
PANEL_BORDER = (170, 166, 156)
TEXT_COLOR = (40, 40, 40)
CREATURE_COLOR = (220, 70, 45)
FOOD_COLOR = (88, 164, 92)
BUTTON_COLOR = (250, 249, 246)
BUTTON_BORDER = (120, 120, 120)
BUTTON_TEXT = (30, 30, 30)
CREATURE_TEXT_COLOR = (255, 248, 240)
PANEL_WIDTH = 220
PANEL_LEFT_PADDING = 20
PANEL_TITLE_TOP = 20
PANEL_STATUS_TOP = 52
STATUS_LINE_HEIGHT = 20
BUTTON_HEIGHT = 34
BUTTON_GAP = 10
BUTTON_TOP_GAP = 16
FOOD_RESPAWN_MS = 5000
FOOD_RADIUS_PX = 5
CTRL_MODS = pygame.KMOD_CTRL | pygame.KMOD_META


@dataclass
class Button:
    label: str
    rect: pygame.Rect


def screenshot_path(screenshot_dir: str) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return Path(screenshot_dir) / f"{timestamp}.png"


def build_status_lines(sim: Simulation, playing: bool, fps: int) -> list[str]:
    largest_mass = max(creature.mass for creature in sim.creatures)
    return [
        f"Tick: {sim.tick}",
        f"Creature Count: {len(sim.creatures)}",
        f"Food Count: {len(sim.food)}",
        f"State: {'playing' if playing else 'paused'}",
        f"FPS: {fps}",
        f"World: {sim.world.width:.0f} x {sim.world.height:.0f}",
        f"Mass0: {sim.creatures[0].mass:.2f}",
        f"Largest Creature: {largest_mass:.2f}",
        f"x0={sim.creatures[0].x:.2f}",
        f"y0={sim.creatures[0].y:.2f}",
    ]


def click_repeats(mods: int) -> int:
    if mods & pygame.KMOD_SHIFT:
        return 100
    if mods & CTRL_MODS:
        return 10
    return 1


def creature_radius_px(base_radius_px: int, creature_mass: float) -> int:
    return max(2, int(base_radius_px * sqrt(creature_mass)))


def apply_button_action(
    clicked: str | None,
    sim: Simulation,
    config: SimulationConfig,
    current_fps: int,
    playing: bool,
    screenshot_dir: str,
    screen: pygame.Surface | None,
    mods: int = 0,
    food_respawn_elapsed_ms: int = 0,
) -> tuple[Simulation, int, bool, str, bool, int]:
    screenshot_message = ""
    running = True
    repeats = click_repeats(mods)

    if clicked == "Play":
        playing = True
    elif clicked == "Pause":
        playing = False
    elif clicked == "Step":
        for _ in range(repeats):
            sim.step()
    elif clicked == "Reset":
        sim = Simulation(config)
        food_respawn_elapsed_ms = 0
    elif clicked == "More Creatures":
        for _ in range(repeats):
            sim.add_creature()
    elif clicked == "Fewer Creatures":
        for _ in range(repeats):
            sim.remove_creature()
    elif clicked == "More Food":
        for _ in range(repeats):
            sim.add_food()
    elif clicked == "Less Food":
        for _ in range(repeats):
            sim.remove_food()
    elif clicked == "Faster":
        current_fps = min(current_fps + 2 * repeats, 120)
    elif clicked == "Slower":
        current_fps = max(current_fps - 2 * repeats, 1)
    elif clicked == "Screenshot" and screen is not None:
        path = screenshot_path(screenshot_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(screen, str(path))
        screenshot_message = f"Saved {path.name}"
    elif clicked == "Quit":
        running = False

    return sim, current_fps, playing, screenshot_message, running, food_respawn_elapsed_ms


def build_buttons(world_width_px: int, top: int) -> list[Button]:
    left = world_width_px + PANEL_LEFT_PADDING
    width = PANEL_WIDTH - 40
    labels = [
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

    buttons: list[Button] = []
    for index, label in enumerate(labels):
        y = top + index * (BUTTON_HEIGHT + BUTTON_GAP)
        buttons.append(Button(label=label, rect=pygame.Rect(left, y, width, BUTTON_HEIGHT)))
    return buttons


def run_pygame(
    sim: Simulation,
    config: SimulationConfig,
    ticks: int,
    scale: int,
    fps: int,
    radius_px: int,
    screenshot_dir: str,
) -> None:
    """Run a pygame window with a control panel."""
    pygame.init()
    pygame.font.init()

    world_width_px = int(sim.world.width * scale)
    world_height_px = int(sim.world.height * scale)
    screen = pygame.display.set_mode((world_width_px + PANEL_WIDTH, world_height_px))
    pygame.display.set_caption("evosim - continuous plane")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 24)

    playing = True
    running = True
    current_fps = fps
    screenshot_message = ""
    food_respawn_elapsed_ms = 0

    status = build_status_lines(sim, playing, current_fps)
    buttons_top = PANEL_STATUS_TOP + len(status) * STATUS_LINE_HEIGHT + BUTTON_TOP_GAP
    buttons = build_buttons(world_width_px, buttons_top)

    draw_frame(screen, sim, scale, radius_px, buttons, font, small_font, current_fps, playing, screenshot_message)
    pygame.display.flip()

    while running and sim.tick < ticks:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = button_at_pos(buttons, event.pos)
                sim, current_fps, playing, screenshot_message, running, food_respawn_elapsed_ms = apply_button_action(
                    clicked=clicked,
                    sim=sim,
                    config=config,
                    current_fps=current_fps,
                    playing=playing,
                    screenshot_dir=screenshot_dir,
                    screen=screen,
                    mods=pygame.key.get_mods(),
                    food_respawn_elapsed_ms=food_respawn_elapsed_ms,
                )

        if playing:
            sim.step()
        food_respawn_elapsed_ms += clock.get_time()
        if food_respawn_elapsed_ms >= FOOD_RESPAWN_MS:
            sim.respawn_food()
            food_respawn_elapsed_ms = 0

        draw_frame(
            screen,
            sim,
            scale,
            radius_px,
            buttons,
            font,
            small_font,
            current_fps,
            playing,
            screenshot_message,
        )
        pygame.display.flip()
        clock.tick(current_fps)

    pygame.quit()


def button_at_pos(buttons: list[Button], pos: tuple[int, int]) -> str | None:
    for button in buttons:
        if button.rect.collidepoint(pos):
            return button.label
    return None


def draw_frame(
    screen: pygame.Surface,
    sim: Simulation,
    scale: int,
    radius_px: int,
    buttons: list[Button],
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    fps: int,
    playing: bool,
    screenshot_message: str,
) -> None:
    world_width_px = int(sim.world.width * scale)
    world_height_px = int(sim.world.height * scale)

    world_rect = pygame.Rect(0, 0, world_width_px, world_height_px)
    panel_rect = pygame.Rect(world_width_px, 0, PANEL_WIDTH, world_height_px)

    pygame.draw.rect(screen, BACKGROUND, world_rect)
    pygame.draw.rect(screen, PANEL_BACKGROUND, panel_rect)
    pygame.draw.line(screen, PANEL_BORDER, (world_width_px, 0), (world_width_px, world_height_px), 2)

    for creature in sim.creatures:
        x_px = int(creature.x * scale)
        y_px = int(creature.y * scale)
        current_radius_px = creature_radius_px(radius_px, creature.mass)
        pygame.draw.circle(screen, CREATURE_COLOR, (x_px, y_px), current_radius_px)
        count_label = small_font.render(str(creature.food_eaten), True, CREATURE_TEXT_COLOR)
        count_rect = count_label.get_rect(center=(x_px, y_px))
        screen.blit(count_label, count_rect)

    for pellet in sim.food:
        x_px = int(pellet.x * scale)
        y_px = int(pellet.y * scale)
        pygame.draw.circle(screen, FOOD_COLOR, (x_px, y_px), FOOD_RADIUS_PX)

    title = font.render("Control Panel", True, TEXT_COLOR)
    screen.blit(title, (world_width_px + PANEL_LEFT_PADDING, PANEL_TITLE_TOP))

    status = build_status_lines(sim, playing, fps)
    for index, line in enumerate(status):
        text = small_font.render(line, True, TEXT_COLOR)
        screen.blit(text, (world_width_px + PANEL_LEFT_PADDING, PANEL_STATUS_TOP + index * STATUS_LINE_HEIGHT))

    for button in buttons:
        pygame.draw.rect(screen, BUTTON_COLOR, button.rect, border_radius=6)
        pygame.draw.rect(screen, BUTTON_BORDER, button.rect, width=2, border_radius=6)
        label = small_font.render(button.label, True, BUTTON_TEXT)
        label_rect = label.get_rect(center=button.rect.center)
        screen.blit(label, label_rect)

    if screenshot_message:
        text = small_font.render(screenshot_message, True, TEXT_COLOR)
        screen.blit(text, (world_width_px + PANEL_LEFT_PADDING, world_height_px - 28))
