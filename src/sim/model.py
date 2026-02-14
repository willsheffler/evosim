from dataclasses import dataclass


@dataclass
class World:
    """A simple 2D continuous world."""

    width: float
    height: float


@dataclass
class Creature:
    """A creature with a position on a continuous plane."""

    x: float
    y: float

    def move(self, world: World, dx: float, dy: float) -> None:
        """Move once using wrap-around boundaries."""
        self.x = (self.x + dx) % world.width
        self.y = (self.y + dy) % world.height
