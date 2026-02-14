from dataclasses import dataclass
from math import cos, pi, sin
from random import Random

from sim.model import Creature, World


@dataclass
class SimulationConfig:
    width: float = 20.0
    height: float = 20.0
    seed: int = 7
    speed: float = 0.8


class Simulation:
    """A tiny deterministic simulation with one creature on a continuous plane."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.world = World(width=config.width, height=config.height)
        self.tick = 0
        self._rng = Random(config.seed)
        self.creature = self._spawn_creature()

    def _spawn_creature(self) -> Creature:
        # Seeded RNG gives the same start position for the same config seed.
        start_x = self._rng.random() * self.world.width
        start_y = self._rng.random() * self.world.height
        return Creature(x=start_x, y=start_y)

    def step(self) -> None:
        angle = self._rng.random() * 2.0 * pi
        dx = self.config.speed * cos(angle)
        dy = self.config.speed * sin(angle)
        self.creature.move(self.world, dx, dy)
        self.tick += 1

    def run(self, ticks: int) -> list[tuple[float, float]]:
        positions: list[tuple[float, float]] = []
        for _ in range(ticks):
            self.step()
            positions.append((self.creature.x, self.creature.y))
        return positions
