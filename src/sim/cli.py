import argparse

from sim.simulation import Simulation, SimulationConfig
from sim.text_render import format_creature_position


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a tiny deterministic creature sim.")
    parser.add_argument(
        "--mode",
        choices=("text", "pygame"),
        default="pygame",
        help="Run in text mode or pygame graphics mode",
    )
    parser.add_argument("--width", type=float, default=40.0, help="World width (continuous units)")
    parser.add_argument("--height", type=float, default=30.0, help="World height (continuous units)")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for reproducible start")
    parser.add_argument("--ticks", type=int, default=456778760, help="How many steps to run")
    parser.add_argument("--speed", type=float, default=0.08, help="Movement speed in world units per tick")
    parser.add_argument("--creatures", type=int, default=50, help="Number of creatures")
    parser.add_argument("--food", type=int, default=250, help="Number of food pellets")
    parser.add_argument("--scale", type=int, default=30, help="Pixels per world unit in pygame mode")
    parser.add_argument("--fps", type=int, default=120, help="Frames per second in pygame mode")
    parser.add_argument("--radius", type=int, default=8, help="Creature circle radius in pixels")
    parser.add_argument(
        "--screenshot-dir",
        type=str,
        default="screenshots",
        help="Directory for screenshot button saves in pygame mode",
    )
    parser.add_argument(
        "--show-coords",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Print x, y coordinates each tick in text mode (default: true)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = SimulationConfig(
        width=args.width,
        height=args.height,
        seed=args.seed,
        speed=args.speed,
        creatures=args.creatures,
        food=args.food,
    )
    sim = Simulation(config)

    if args.mode == "pygame":
        from sim.pygame_view import run_pygame

        run_pygame(
            sim=sim,
            config=config,
            ticks=args.ticks,
            scale=args.scale,
            fps=args.fps,
            radius_px=args.radius,
            screenshot_dir=args.screenshot_dir,
        )
        return

    first_creature = sim.creatures[0]
    print(
        f"Start: tick={sim.tick}, {format_creature_position(first_creature)}, "
        f"world={sim.world.width:.1f}x{sim.world.height:.1f}, seed={args.seed}, "
        f"speed={args.speed}, creatures={len(sim.creatures)}"
    )
    for _ in range(args.ticks):
        sim.step()
        if args.show_coords:
            print(f"Tick {sim.tick:>2}: {format_creature_position(sim.creatures[0])}")


if __name__ == "__main__":
    main()
