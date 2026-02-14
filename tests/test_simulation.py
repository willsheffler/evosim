from sim.simulation import Simulation, SimulationConfig


def test_simulation_is_deterministic_for_same_seed() -> None:
    config = SimulationConfig(width=20, height=20, seed=42)
    sim_a = Simulation(config)
    sim_b = Simulation(config)

    assert (sim_a.creature.x, sim_a.creature.y) == (sim_b.creature.x, sim_b.creature.y)

    for _ in range(12):
        sim_a.step()
        sim_b.step()
        assert (sim_a.creature.x, sim_a.creature.y) == (sim_b.creature.x, sim_b.creature.y)


def test_wrap_around_boundary() -> None:
    config = SimulationConfig(width=3.0, height=3.0, seed=1, speed=0.8)
    sim = Simulation(config)
    sim.creature.x = 2.9
    sim.creature.y = 0.2
    sim.creature.move(sim.world, dx=0.5, dy=0.0)

    assert abs(sim.creature.x - 0.4) < 1e-9
    assert abs(sim.creature.y - 0.2) < 1e-9
