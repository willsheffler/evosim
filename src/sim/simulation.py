from dataclasses import dataclass
from math import atan2, cos, dist, pi, sin, sqrt
from random import Random

from sim.model import Creature, Food, World


CREATURE_RADIUS = 0.35
FOOD_RADIUS = 0.18
GROWTH_FACTOR = 1.1
MID_GROWTH_FACTOR = 1.05
LOW_GROWTH_FACTOR = 1.01
MAX_GROWTH_FOOD_EATEN = 150
SPEED_LOSS_PER_FOOD = 0.01
FOOD_BIAS_STRENGTH = 0.7
PREY_BIAS_STRENGTH = 1.0
PREDATOR_AVOID_STRENGTH = 0.9
RANDOM_WANDER_STRENGTH = 0.25
MAX_CREATURE_AWARENESS_MULTIPLIER = 5.0
MIN_CREATURE_AWARENESS_MULTIPLIER = 3.0
AWARENESS_FOOD_START = 10
AWARENESS_FOOD_END = 50


@dataclass
class SimulationConfig:
    width: float = 20.0
    height: float = 20.0
    seed: int = 7
    speed: float = 0.8
    creatures: int = 50
    food: int = 250


class Simulation:
    """A tiny deterministic simulation with creatures on a continuous plane."""

    def __init__(self, config: SimulationConfig) -> None:
        if config.creatures < 1:
            raise ValueError("creatures must be at least 1")
        if config.food < 0:
            raise ValueError("food must be at least 0")
        self.config = config
        self.world = World(width=config.width, height=config.height)
        self.tick = 0
        self._rng = Random(config.seed)
        self.creatures = [self._spawn_creature() for _ in range(config.creatures)]
        self.food = [self._spawn_food() for _ in range(config.food)]

    def _spawn_creature(self) -> Creature:
        # Seeded RNG gives the same start position for the same config seed.
        start_x = self._rng.random() * self.world.width
        start_y = self._rng.random() * self.world.height
        return Creature(x=start_x, y=start_y)

    def _spawn_food(self) -> Food:
        return Food(
            x=self._rng.random() * self.world.width,
            y=self._rng.random() * self.world.height,
        )

    def creature_radius(self, creature: Creature) -> float:
        return CREATURE_RADIUS * sqrt(creature.mass)

    def creature_size(self, creature: Creature) -> int:
        return creature.food_eaten

    def movement_speed(self, creature: Creature) -> float:
        slowdown_food_eaten = min(creature.food_eaten, MAX_GROWTH_FOOD_EATEN)
        return self.config.speed * ((1.0 - SPEED_LOSS_PER_FOOD) ** slowdown_food_eaten)

    def growth_factor(self, creature: Creature) -> float:
        if creature.food_eaten >= MAX_GROWTH_FOOD_EATEN:
            return 1.0
        if creature.food_eaten >= 40:
            return LOW_GROWTH_FACTOR
        if creature.food_eaten >= 25:
            return MID_GROWTH_FACTOR
        return GROWTH_FACTOR

    def nearest_food(self, creature: Creature) -> Food | None:
        if not self.food:
            return None
        return min(self.food, key=lambda pellet: dist((creature.x, creature.y), (pellet.x, pellet.y)))

    def creature_awareness_multiplier(self, creature: Creature) -> float:
        if creature.food_eaten <= AWARENESS_FOOD_START:
            return MAX_CREATURE_AWARENESS_MULTIPLIER
        if creature.food_eaten >= AWARENESS_FOOD_END:
            return MIN_CREATURE_AWARENESS_MULTIPLIER

        progress = (creature.food_eaten - AWARENESS_FOOD_START) / (AWARENESS_FOOD_END - AWARENESS_FOOD_START)
        return MAX_CREATURE_AWARENESS_MULTIPLIER - progress * (
            MAX_CREATURE_AWARENESS_MULTIPLIER - MIN_CREATURE_AWARENESS_MULTIPLIER
        )

    def nearest_smaller_creature(self, creature: Creature) -> Creature | None:
        awareness_radius = self.creature_awareness_multiplier(creature) * self.creature_radius(creature)
        smaller_creatures = [
            other
            for other in self.creatures
            if other is not creature
            and self.creature_size(other) < self.creature_size(creature)
            and dist((creature.x, creature.y), (other.x, other.y)) <= awareness_radius
        ]
        if not smaller_creatures:
            return None
        return min(smaller_creatures, key=lambda other: dist((creature.x, creature.y), (other.x, other.y)))

    def nearest_larger_creature(self, creature: Creature) -> Creature | None:
        awareness_radius = self.creature_awareness_multiplier(creature) * self.creature_radius(creature)
        larger_creatures = [
            other
            for other in self.creatures
            if other is not creature
            and self.creature_size(other) > self.creature_size(creature)
            and dist((creature.x, creature.y), (other.x, other.y)) <= awareness_radius
        ]
        if not larger_creatures:
            return None
        return min(larger_creatures, key=lambda other: dist((creature.x, creature.y), (other.x, other.y)))

    def movement_angle(self, creature: Creature) -> float:
        random_angle = self._rng.random() * 2.0 * pi
        move_dx = RANDOM_WANDER_STRENGTH * cos(random_angle)
        move_dy = RANDOM_WANDER_STRENGTH * sin(random_angle)

        nearest_food = self.nearest_food(creature)
        if nearest_food is not None:
            food_angle = atan2(nearest_food.y - creature.y, nearest_food.x - creature.x)
            move_dx += FOOD_BIAS_STRENGTH * cos(food_angle)
            move_dy += FOOD_BIAS_STRENGTH * sin(food_angle)

        nearest_smaller = self.nearest_smaller_creature(creature)
        if nearest_smaller is not None:
            prey_angle = atan2(nearest_smaller.y - creature.y, nearest_smaller.x - creature.x)
            move_dx += PREY_BIAS_STRENGTH * cos(prey_angle)
            move_dy += PREY_BIAS_STRENGTH * sin(prey_angle)

        nearest_larger = self.nearest_larger_creature(creature)
        if nearest_larger is not None:
            predator_angle = atan2(nearest_larger.y - creature.y, nearest_larger.x - creature.x)
            move_dx -= PREDATOR_AVOID_STRENGTH * cos(predator_angle)
            move_dy -= PREDATOR_AVOID_STRENGTH * sin(predator_angle)

        return atan2(move_dy, move_dx)

    def add_creature(self) -> None:
        self.creatures.append(self._spawn_creature())
        self.config.creatures = len(self.creatures)

    def remove_creature(self) -> None:
        if len(self.creatures) <= 1:
            return
        self.creatures.pop()
        self.config.creatures = len(self.creatures)

    def add_food(self) -> None:
        self.food.append(self._spawn_food())
        self.config.food = len(self.food)

    def remove_food(self) -> None:
        if not self.food:
            return
        self.food.pop()
        self.config.food = len(self.food)

    def respawn_food(self) -> None:
        while len(self.food) < self.config.food:
            self.food.append(self._spawn_food())

    def feed_creature(self, creature: Creature, food_units: int = 1) -> None:
        for _ in range(food_units):
            creature.mass *= self.growth_factor(creature)
            creature.food_eaten += 1

    def _eat_overlapping_food(self, creature: Creature) -> None:
        surviving_food: list[Food] = []
        for pellet in self.food:
            distance = dist((creature.x, creature.y), (pellet.x, pellet.y))
            max_distance = self.creature_radius(creature) + FOOD_RADIUS
            if distance <= max_distance:
                self.feed_creature(creature)
            else:
                surviving_food.append(pellet)
        self.food = surviving_food

    def _resolve_creature_overlaps(self) -> None:
        changed = True
        while changed and len(self.creatures) > 1:
            changed = False
            for index, creature in enumerate(self.creatures):
                for other_index in range(index + 1, len(self.creatures)):
                    other = self.creatures[other_index]
                    overlap_distance = self.creature_radius(creature) + self.creature_radius(other)
                    distance = dist((creature.x, creature.y), (other.x, other.y))
                    creature_size = self.creature_size(creature)
                    other_size = self.creature_size(other)
                    if distance > overlap_distance or creature_size == other_size:
                        continue
                    if creature_size > other_size:
                        self.feed_creature(creature, 1 + other.food_eaten // 2)
                        self.creatures.pop(other_index)
                    else:
                        self.feed_creature(other, 1 + creature.food_eaten // 2)
                        self.creatures.pop(index)
                    changed = True
                    break
                if changed:
                    break

    def step(self) -> None:
        for creature in self.creatures:
            angle = self.movement_angle(creature)
            speed = self.movement_speed(creature)
            dx = speed * cos(angle)
            dy = speed * sin(angle)
            creature.move(self.world, dx, dy)
            self._eat_overlapping_food(creature)
        self._resolve_creature_overlaps()
        self.tick += 1

    def run(self, ticks: int) -> list[list[tuple[float, float]]]:
        positions: list[list[tuple[float, float]]] = []
        for _ in range(ticks):
            self.step()
            positions.append([(creature.x, creature.y) for creature in self.creatures])
        return positions
