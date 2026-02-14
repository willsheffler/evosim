from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pygame

from sim.simulation import Simulation, SimulationConfig


BACKGROUND = (245, 244, 238)
PANEL_BACKGROUND = (230, 227, 220)
PANEL_BORDER = (170, 166, 156)
TEXT_COLOR = (40, 40, 40)
CREATURE_COLOR = (220, 70, 45)
BUTTON_COLOR = (250, 249, 246)
BUTTON_BORDER = (120, 120, 120)
BUTTON_TEXT = (30, 30, 30)
PANEL_WIDTH = 220


@dataclass
class Button:
    label: str
    rect: pygame.Rect


def screenshot_path(screenshot_dir: str) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return Path(screenshot_dir) / f"{timestamp}.png"


def build_buttons(world_width_px: int) -> list[Button]:
    left = world_width_px + 20
    top = 90
    width = PANEL_WIDTH - 40
    height = 34
    gap = 10
    labels = ["Play", "Pause", "Step", "Reset", "Faster", "Slower", "Screenshot", "Quit"]

    buttons: list[Button] = []
    for index, label in enumerate(labels):
        y = top + index * (height + gap)
        buttons.append(Button(label=label, rect=pygame.Rect(left, y, width, height)))
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
    buttons = build_buttons(world_width_px)

    playing = True
    running = True
    current_fps = fps
    screenshot_message = ""

    draw_frame(screen, sim, scale, radius_px, buttons, font, small_font, current_fps, playing, screenshot_message)
    pygame.display.flip()

    while running and sim.tick < ticks:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = button_at_pos(buttons, event.pos)
                if clicked == "Play":
                    playing = True
                elif clicked == "Pause":
                    playing = False
                elif clicked == "Step":
                    sim.step()
                elif clicked == "Reset":
                    sim = Simulation(config)
                elif clicked == "Faster":
                    current_fps = min(current_fps + 2, 120)
                elif clicked == "Slower":
                    current_fps = max(current_fps - 2, 1)
                elif clicked == "Screenshot":
                    path = screenshot_path(screenshot_dir)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    pygame.image.save(screen, str(path))
                    screenshot_message = f"Saved {path.name}"
                elif clicked == "Quit":
                    running = False

        if playing:
            sim.step()

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
        pygame.draw.circle(screen, CREATURE_COLOR, (x_px, y_px), radius_px)

    title = font.render("Control Panel", True, TEXT_COLOR)
    screen.blit(title, (world_width_px + 20, 20))

    status = [
        f"Tick: {sim.tick}",
        f"Creatures: {len(sim.creatures)}",
        f"State: {'playing' if playing else 'paused'}",
        f"FPS: {fps}",
        f"x0={sim.creatures[0].x:.2f}",
        f"y0={sim.creatures[0].y:.2f}",
    ]
    for index, line in enumerate(status):
        text = small_font.render(line, True, TEXT_COLOR)
        screen.blit(text, (world_width_px + 20, 52 + index * 20))

    for button in buttons:
        pygame.draw.rect(screen, BUTTON_COLOR, button.rect, border_radius=6)
        pygame.draw.rect(screen, BUTTON_BORDER, button.rect, width=2, border_radius=6)
        label = small_font.render(button.label, True, BUTTON_TEXT)
        label_rect = label.get_rect(center=button.rect.center)
        screen.blit(label, label_rect)

    if screenshot_message:
        text = small_font.render(screenshot_message, True, TEXT_COLOR)
        screen.blit(text, (world_width_px + 20, world_height_px - 28))
