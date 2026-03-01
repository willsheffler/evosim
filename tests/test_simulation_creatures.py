from math import cos

from sim.simulation import Simulation, SimulationConfig


def test_add_creature_increases_count_and_updates_config() -> None:
    sim = Simulation(SimulationConfig(creatures=2, seed=7))

    sim.add_creature()

    assert len(sim.creatures) == 3
    assert sim.config.creatures == 3


def test_remove_creature_decreases_count_and_updates_config() -> None:
    sim = Simulation(SimulationConfig(creatures=3, seed=7))

    sim.remove_creature()

    assert len(sim.creatures) == 2
    assert sim.config.creatures == 2


def test_remove_creature_keeps_at_least_one() -> None:
    sim = Simulation(SimulationConfig(creatures=1, seed=7))

    sim.remove_creature()

    assert len(sim.creatures) == 1
    assert sim.config.creatures == 1


def test_add_food_increases_count_and_updates_config() -> None:
    sim = Simulation(SimulationConfig(food=2, seed=7))

    sim.add_food()

    assert len(sim.food) == 3
    assert sim.config.food == 3


def test_remove_food_decreases_count_and_updates_config() -> None:
    sim = Simulation(SimulationConfig(food=3, seed=7))

    sim.remove_food()

    assert len(sim.food) == 2
    assert sim.config.food == 2


def test_remove_food_stops_at_zero() -> None:
    sim = Simulation(SimulationConfig(food=0, seed=7))

    sim.remove_food()

    assert len(sim.food) == 0
    assert sim.config.food == 0


def test_eating_food_grows_creature_and_removes_food() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=1, seed=7, speed=0.0))
    sim.creatures[0].x = 5.0
    sim.creatures[0].y = 5.0
    sim.food[0].x = 5.0
    sim.food[0].y = 5.0

    sim.step()

    assert sim.creatures[0].mass == 1.1
    assert sim.creatures[0].food_eaten == 1
    assert len(sim.food) == 0
    assert sim.config.food == 1


def test_creatures_start_with_zero_food_eaten() -> None:
    sim = Simulation(SimulationConfig(creatures=2, food=0, seed=7))

    assert [creature.food_eaten for creature in sim.creatures] == [0, 0]
    assert [creature.mass for creature in sim.creatures] == [1.0, 1.0]


def test_creature_awareness_starts_at_five_times_radius() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7))

    assert sim.creature_awareness_multiplier(sim.creatures[0]) == 5.0


def test_creature_awareness_stays_five_times_radius_until_ten_food() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7))
    sim.creatures[0].food_eaten = 10

    assert sim.creature_awareness_multiplier(sim.creatures[0]) == 5.0


def test_creature_awareness_shrinks_between_ten_and_fifty_food() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7))
    sim.creatures[0].food_eaten = 30

    assert sim.creature_awareness_multiplier(sim.creatures[0]) == 4.0


def test_creature_awareness_stops_at_three_times_radius_after_fifty_food() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7))
    sim.creatures[0].food_eaten = 50

    assert sim.creature_awareness_multiplier(sim.creatures[0]) == 3.0


def test_creature_radius_uses_square_root_of_mass() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7))
    sim.creatures[0].mass = 4.0

    assert sim.creature_radius(sim.creatures[0]) == 0.7


def test_creature_size_matches_food_eaten_even_past_150() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7))
    sim.creatures[0].food_eaten = 200

    assert sim.creature_size(sim.creatures[0]) == 200


def test_movement_speed_drops_one_percent_per_food_eaten() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7, speed=1.0))
    sim.creatures[0].food_eaten = 10

    assert sim.movement_speed(sim.creatures[0]) == 0.99**10


def test_movement_speed_stays_above_zero_after_many_food() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7, speed=1.0))
    sim.creatures[0].food_eaten = 200

    assert sim.movement_speed(sim.creatures[0]) > 0.0


def test_movement_speed_stops_decreasing_after_150_food_eaten() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7, speed=1.0))
    sim.creatures[0].food_eaten = 150
    speed_at_150 = sim.movement_speed(sim.creatures[0])

    sim.creatures[0].food_eaten = 200

    assert sim.movement_speed(sim.creatures[0]) == speed_at_150


def test_creatures_bias_toward_nearest_food() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=1, seed=7, speed=1.0))
    sim.creatures[0].x = 5.0
    sim.creatures[0].y = 5.0
    sim.food[0].x = 8.0
    sim.food[0].y = 5.0

    angle = sim.movement_angle(sim.creatures[0])

    assert cos(angle) > 0


def test_bigger_creatures_bias_toward_smaller_creatures() -> None:
    sim = Simulation(SimulationConfig(creatures=2, food=0, seed=7, speed=1.0))
    sim.creatures[0].x = 5.0
    sim.creatures[0].y = 5.0
    sim.creatures[0].food_eaten = 20
    sim.creatures[1].x = 6.0
    sim.creatures[1].y = 5.0
    sim.creatures[1].food_eaten = 3

    angle = sim.movement_angle(sim.creatures[0])

    assert cos(angle) > 0
    assert sim.nearest_smaller_creature(sim.creatures[0]) is sim.creatures[1]


def test_smaller_creatures_bias_away_from_bigger_creatures() -> None:
    sim = Simulation(SimulationConfig(creatures=2, food=0, seed=7, speed=1.0))
    sim.creatures[0].x = 5.0
    sim.creatures[0].y = 5.0
    sim.creatures[0].food_eaten = 3
    sim.creatures[1].x = 5.6
    sim.creatures[1].y = 5.0
    sim.creatures[1].food_eaten = 20

    angle = sim.movement_angle(sim.creatures[0])

    assert cos(angle) < 0


def test_creatures_do_not_target_smaller_creatures_outside_awareness_range() -> None:
    sim = Simulation(SimulationConfig(creatures=2, food=0, seed=7, speed=1.0))
    sim.creatures[0].x = 5.0
    sim.creatures[0].y = 5.0
    sim.creatures[0].food_eaten = 20
    sim.creatures[1].x = 9.0
    sim.creatures[1].y = 5.0
    sim.creatures[1].food_eaten = 3

    assert sim.nearest_smaller_creature(sim.creatures[0]) is None


def test_creatures_do_not_flee_larger_creatures_outside_awareness_range() -> None:
    sim = Simulation(SimulationConfig(creatures=2, food=0, seed=7, speed=1.0))
    sim.creatures[0].x = 5.0
    sim.creatures[0].y = 5.0
    sim.creatures[0].food_eaten = 3
    sim.creatures[1].x = 8.0
    sim.creatures[1].y = 5.0
    sim.creatures[1].food_eaten = 20

    assert sim.nearest_larger_creature(sim.creatures[0]) is None


def test_larger_creature_eats_smaller_creature_on_overlap() -> None:
    sim = Simulation(SimulationConfig(creatures=2, food=0, seed=7, speed=0.0))
    sim.creatures[0].x = 5.0
    sim.creatures[0].y = 5.0
    sim.creatures[0].mass = 4.0
    sim.creatures[0].food_eaten = 12
    sim.creatures[1].x = 5.0
    sim.creatures[1].y = 5.0
    sim.creatures[1].mass = 1.0
    sim.creatures[1].food_eaten = 9

    sim.step()

    assert len(sim.creatures) == 1
    assert sim.creatures[0].mass > 4.0
    assert sim.creatures[0].food_eaten == 17


def test_smaller_creature_food_bonus_rounds_down_when_eaten() -> None:
    sim = Simulation(SimulationConfig(creatures=2, food=0, seed=7, speed=0.0))
    sim.creatures[0].x = 5.0
    sim.creatures[0].y = 5.0
    sim.creatures[0].mass = 5.0
    sim.creatures[0].food_eaten = 8
    sim.creatures[1].x = 5.0
    sim.creatures[1].y = 5.0
    sim.creatures[1].mass = 1.0
    sim.creatures[1].food_eaten = 5

    sim.step()

    assert len(sim.creatures) == 1
    assert sim.creatures[0].food_eaten == 11
    assert sim.creatures[0].mass > 5.0


def test_creatures_above_150_still_compare_by_displayed_number() -> None:
    sim = Simulation(SimulationConfig(creatures=2, food=0, seed=7, speed=1.0))
    sim.creatures[0].x = 5.0
    sim.creatures[0].y = 5.0
    sim.creatures[0].food_eaten = 170
    sim.creatures[1].x = 5.5
    sim.creatures[1].y = 5.0
    sim.creatures[1].food_eaten = 200

    assert sim.nearest_smaller_creature(sim.creatures[1]) is sim.creatures[0]
    assert sim.nearest_larger_creature(sim.creatures[0]) is sim.creatures[1]


def test_eating_creature_slows_predator_like_food_does() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7, speed=1.0))
    sim.creatures[0].mass = 4.0
    sim.creatures[0].food_eaten = 0
    speed_before = sim.movement_speed(sim.creatures[0])

    sim.feed_creature(sim.creatures[0], food_units=5)

    assert sim.movement_speed(sim.creatures[0]) < speed_before


def test_equal_mass_creatures_do_not_eat_each_other() -> None:
    sim = Simulation(SimulationConfig(creatures=2, food=0, seed=7, speed=0.0))
    sim.creatures[0].x = 5.0
    sim.creatures[0].y = 5.0
    sim.creatures[0].mass = 2.0
    sim.creatures[1].x = 5.0
    sim.creatures[1].y = 5.0
    sim.creatures[1].mass = 2.0

    sim.step()

    assert len(sim.creatures) == 2


def test_growth_factor_slows_after_25_food_eaten() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7))
    sim.creatures[0].food_eaten = 25

    assert sim.growth_factor(sim.creatures[0]) == 1.05


def test_growth_factor_slows_further_after_40_food_eaten() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7))
    sim.creatures[0].food_eaten = 40

    assert sim.growth_factor(sim.creatures[0]) == 1.01


def test_growth_factor_stops_after_150_food_eaten() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=0, seed=7))
    sim.creatures[0].food_eaten = 150

    assert sim.growth_factor(sim.creatures[0]) == 1.0


def test_eating_food_after_150_only_increases_counter() -> None:
    sim = Simulation(SimulationConfig(creatures=1, food=1, seed=7, speed=0.0))
    sim.creatures[0].x = 5.0
    sim.creatures[0].y = 5.0
    sim.creatures[0].food_eaten = 150
    sim.creatures[0].mass = 99.0
    sim.food[0].x = 5.0
    sim.food[0].y = 5.0

    sim.step()

    assert sim.creatures[0].mass == 99.0
    assert sim.creatures[0].food_eaten == 151


def test_respawn_food_refills_to_configured_target() -> None:
    sim = Simulation(SimulationConfig(food=2, creatures=1, seed=7, speed=0.0))
    sim.food = []

    sim.respawn_food()

    assert len(sim.food) == 2
