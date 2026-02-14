from sim.model import Creature
from sim.text_render import format_creature_position


def test_format_creature_position_rounds_to_two_decimals() -> None:
    creature = Creature(x=2.345, y=1.234)

    text = format_creature_position(creature)

    assert text == "x=2.35, y=1.23"
