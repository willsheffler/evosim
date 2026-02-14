from sim.pygame_view import build_buttons, screenshot_path


def test_build_buttons_creates_numerous_controls() -> None:
    buttons = build_buttons(world_width_px=600)
    labels = [button.label for button in buttons]
    assert labels == ["Play", "Pause", "Step", "Reset", "Faster", "Slower", "Screenshot", "Quit"]


def test_screenshot_path_uses_png_in_directory() -> None:
    path = screenshot_path("screenshots")
    assert path.parent.name == "screenshots"
    assert path.suffix == ".png"
