from sim.simulation import Simulation, SimulationConfig
import pytest


def test_simulation_is_deterministic_for_same_seed() -> None:
    config = SimulationConfig(width=20, height=20, seed=42, creatures=5)
    sim_a = Simulation(config)
    sim_b = Simulation(config)

    assert len(sim_a.creatures) == 5
    assert len(sim_b.creatures) == 5
    assert [(c.x, c.y) for c in sim_a.creatures] == [(c.x, c.y) for c in sim_b.creatures]

    for _ in range(12):
        sim_a.step()
        sim_b.step()
        assert [(c.x, c.y) for c in sim_a.creatures] == [(c.x, c.y) for c in sim_b.creatures]


def test_wrap_around_boundary() -> None:
    config = SimulationConfig(width=3.0, height=3.0, seed=1, speed=0.8, creatures=1)
    sim = Simulation(config)
    sim.creatures[0].x = 2.9
    sim.creatures[0].y = 0.2
    sim.creatures[0].move(sim.world, dx=0.5, dy=0.0)

    assert abs(sim.creatures[0].x - 0.4) < 1e-9
    assert abs(sim.creatures[0].y - 0.2) < 1e-9


def test_creatures_must_be_at_least_one() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        Simulation(SimulationConfig(creatures=0))
