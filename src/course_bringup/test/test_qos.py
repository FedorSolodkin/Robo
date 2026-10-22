from course_bringup.qos import make_qos, parse_reliability
import pytest
from rclpy.qos import QoSHistoryPolicy, QoSReliabilityPolicy


def test_parse_known_names():
    assert parse_reliability('reliable') == QoSReliabilityPolicy.RELIABLE
    assert parse_reliability('best_effort') == QoSReliabilityPolicy.BEST_EFFORT


@pytest.mark.parametrize('bad', ['', 'RELIABLE', 'besteffort', None, 1, True])
def test_parse_rejects_anything_else(bad):
    with pytest.raises(ValueError):
        parse_reliability(bad)


def test_profile_is_keep_last_depth_10():
    qos = make_qos('best_effort')
    assert qos.history == QoSHistoryPolicy.KEEP_LAST
    assert qos.depth == 10
    assert qos.reliability == QoSReliabilityPolicy.BEST_EFFORT
    assert make_qos('reliable').reliability == QoSReliabilityPolicy.RELIABLE
