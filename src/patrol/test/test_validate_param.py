from patrol.patrol import validate_param
import pytest


@pytest.mark.parametrize('name, value', [
    ('linear_speed', 0.0),
    ('linear_speed', 0.5),
    ('linear_speed', 1.0),
    ('turn_rate', -1.0),
    ('turn_rate', 0.3),
    ('turn_rate', 1.0),
    ('publish_hz', 1.0),
    ('publish_hz', 5.0),
    ('publish_hz', 10.0),
    ('publish_hz', 30.0),
])
def test_accepts_values_inside_the_range(name, value):
    assert validate_param(name, value) == (True, '')


@pytest.mark.parametrize('name, value', [
    ('linear_speed', -0.1),
    ('linear_speed', 1.1),
    ('turn_rate', -1.1),
    ('turn_rate', 1.1),
    ('publish_hz', 0.0),
    ('publish_hz', -5.0),
    ('publish_hz', 0.9),
    ('publish_hz', 30.1),
])
def test_rejects_values_outside_the_range(name, value):
    ok, reason = validate_param(name, value)
    assert ok is False
    assert name in reason


@pytest.mark.parametrize('value', [float('nan'), float('inf'), float('-inf')])
def test_rejects_non_finite_values(value):
    ok, reason = validate_param('publish_hz', value)
    assert ok is False
    assert 'finite' in reason


@pytest.mark.parametrize('value', ['fast', None, True])
def test_rejects_non_numeric_values(value):
    ok, reason = validate_param('linear_speed', value)
    assert ok is False
    assert 'number' in reason


def test_change_from_10_to_5_hz_is_allowed():
    assert validate_param('publish_hz', 10.0)[0] is True
    assert validate_param('publish_hz', 5.0)[0] is True
