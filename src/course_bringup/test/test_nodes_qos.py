import os
import time

from course_bringup.pose_relay import PoseRelay
from course_bringup.sensor_listener import SensorListener
import pytest
import rclpy
from rclpy.qos import QoSReliabilityPolicy
from turtlesim_msgs.msg import Pose

NS = f'/qos_test_{os.getpid()}'
FAKE_POSE = f'{NS}/fake_pose'


def init(*extra):
    # The relay's input is remapped away from /turtle1/pose, so the tests can
    # never mix with a live turtlesim on the same ROS_DOMAIN_ID.
    rclpy.init(args=['--ros-args', '-r', f'__ns:={NS}',
                     '-r', f'/turtle1/pose:={FAKE_POSE}', *extra])


def spin_until(nodes, condition, seconds=20.0):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline and not condition():
        for node in nodes:
            rclpy.spin_once(node, timeout_sec=0.05)
    return condition()


def make_source():
    """Plain publisher that stands in for turtlesim's pose stream."""
    source = rclpy.create_node('fake_turtle')
    return source, source.create_publisher(Pose, FAKE_POSE, 10)


@pytest.fixture
def shutdown():
    yield
    rclpy.try_shutdown()


def test_relay_publishes_best_effort_on_a_relative_topic(shutdown):
    init()
    relay = PoseRelay()
    assert relay._pub.topic_name == f'{NS}/sensor_pose'
    assert relay._pub.qos_profile.reliability == QoSReliabilityPolicy.BEST_EFFORT
    assert relay._pub.qos_profile.depth == 10
    relay.destroy_node()


def test_listener_reliability_comes_from_the_parameter(shutdown):
    init('-p', 'reliability:=best_effort')
    listener = SensorListener()
    assert listener._sub.qos_profile.reliability == QoSReliabilityPolicy.BEST_EFFORT
    listener.destroy_node()


def test_listener_default_is_reliable_and_bad_value_is_rejected(shutdown):
    init()
    listener = SensorListener()
    assert listener._sub.qos_profile.reliability == QoSReliabilityPolicy.RELIABLE
    listener.destroy_node()
    rclpy.try_shutdown()
    init('-p', 'reliability:=sometimes')
    with pytest.raises(ValueError):
        SensorListener()


def test_reliable_listener_gets_nothing_and_reports_incompatible_qos(shutdown):
    init()
    source, source_pub = make_source()
    relay = PoseRelay()
    listener = SensorListener()
    nodes = [source, relay, listener]
    assert spin_until(nodes, lambda: listener.incompatible_events > 0)
    for _ in range(20):
        source_pub.publish(Pose())
        spin_until(nodes, lambda: False, 0.05)
    assert listener.received == 0
    for node in nodes:
        node.destroy_node()


def test_best_effort_listener_receives_the_relayed_pose(shutdown):
    init('-p', 'reliability:=best_effort')
    source, source_pub = make_source()
    relay = PoseRelay()
    listener = SensorListener()
    nodes = [source, relay, listener]

    def publish_and_check():
        source_pub.publish(Pose())
        return listener.received > 0

    assert spin_until(nodes, publish_and_check)
    assert listener.incompatible_events == 0
    for node in nodes:
        node.destroy_node()
