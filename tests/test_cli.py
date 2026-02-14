from sim.cli import build_parser


def test_cli_defaults_are_beginner_friendly() -> None:
    args = build_parser().parse_args([])
    assert args.mode == "text"
    assert args.width == 20
    assert args.height == 20
    assert args.seed == 7
    assert args.ticks == 10
    assert args.speed == 0.8
    assert args.scale == 30
    assert args.fps == 6
    assert args.radius == 8
    assert args.screenshot_dir == "screenshots"
    assert args.show_coords is True
