from patrol.patrol import PatrolNode
import pytest
import rclpy
from rclpy.parameter import Parameter


@pytest.fixture
def node():
    rclpy.init()
    patrol = PatrolNode()
    yield patrol
    patrol.destroy_node()
    rclpy.shutdown()


def period_ns(hz):
    return int(1.0 / hz * 1e9)


def test_defaults(node):
    assert node.get_parameter('linear_speed').value == 0.5
    assert node.get_parameter('turn_rate').value == 0.3
    assert node.get_parameter('publish_hz').value == 10.0
    assert node._timer.timer_period_ns == period_ns(10.0)


def test_valid_hz_change_recreates_the_timer(node):
    old_timer = node._timer

    result = node.set_parameters([Parameter('publish_hz', value=5.0)])[0]

    assert result.successful is True
    assert node.get_parameter('publish_hz').value == 5.0
    assert node._timer is not old_timer
    assert node._timer.timer_period_ns == period_ns(5.0)


def test_old_timer_is_stopped_and_only_one_timer_remains(node):
    old_timer = node._timer

    node.set_parameters([Parameter('publish_hz', value=5.0)])

    timers = list(node.timers)
    assert len(timers) == 1
    assert old_timer not in timers


@pytest.mark.parametrize('bad', [0.0, -5.0, float('nan'), float('inf'), 31.0])
def test_bad_hz_is_rejected_and_state_is_kept(node, bad):
    old_timer = node._timer

    result = node.set_parameters([Parameter('publish_hz', value=bad)])[0]

    assert result.successful is False
    assert node.get_parameter('publish_hz').value == 10.0
    assert node._timer is old_timer
    assert node._timer.timer_period_ns == period_ns(10.0)
    assert len(list(node.timers)) == 1


def test_bad_value_in_a_batch_changes_nothing(node):
    old_timer = node._timer

    results = node.set_parameters_atomically([
        Parameter('publish_hz', value=5.0),
        Parameter('linear_speed', value=7.0),
    ])

    assert results.successful is False
    assert node.get_parameter('publish_hz').value == 10.0
    assert node.get_parameter('linear_speed').value == 0.5
    assert node._timer is old_timer


def test_speed_and_turn_changes_are_validated(node):
    assert node.set_parameters([Parameter('linear_speed', value=1.0)])[0].successful
    assert node.set_parameters([Parameter('turn_rate', value=-1.0)])[0].successful
    assert not node.set_parameters([Parameter('turn_rate', value=1.5)])[0].successful
    assert node.get_parameter('turn_rate').value == -1.0


def test_foreign_parameters_are_not_blocked(node):
    result = node.set_parameters([Parameter('use_sim_time', value=False)])[0]
    assert result.successful is True


def test_invalid_startup_value_is_refused():
    rclpy.init(args=['--ros-args', '-p', 'publish_hz:=0.0'])
    try:
        with pytest.raises(ValueError):
            PatrolNode()
    finally:
        rclpy.shutdown()
