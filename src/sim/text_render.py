from sim.model import Creature


def format_creature_position(creature: Creature) -> str:
    """Return beginner-friendly text for continuous x, y coordinates."""
    return f"x={creature.x:.2f}, y={creature.y:.2f}"
