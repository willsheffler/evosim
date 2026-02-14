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
    creatures: int = 8


class Simulation:
    """A tiny deterministic simulation with creatures on a continuous plane."""

    def __init__(self, config: SimulationConfig) -> None:
        if config.creatures < 1:
            raise ValueError("creatures must be at least 1")
        self.config = config
        self.world = World(width=config.width, height=config.height)
        self.tick = 0
        self._rng = Random(config.seed)
        self.creatures = [self._spawn_creature() for _ in range(config.creatures)]

    def _spawn_creature(self) -> Creature:
        # Seeded RNG gives the same start position for the same config seed.
        start_x = self._rng.random() * self.world.width
        start_y = self._rng.random() * self.world.height
        return Creature(x=start_x, y=start_y)

    def step(self) -> None:
        for creature in self.creatures:
            angle = self._rng.random() * 2.0 * pi
            dx = self.config.speed * cos(angle)
            dy = self.config.speed * sin(angle)
            creature.move(self.world, dx, dy)
        self.tick += 1

    def run(self, ticks: int) -> list[list[tuple[float, float]]]:
        positions: list[list[tuple[float, float]]] = []
        for _ in range(ticks):
            self.step()
            positions.append([(creature.x, creature.y) for creature in self.creatures])
        return positions
