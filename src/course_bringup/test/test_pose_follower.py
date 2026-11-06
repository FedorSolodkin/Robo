import os
import time

from course_bringup.pose_follower import pose_changed, PoseFollower
import pytest
import rclpy
from rclpy.qos import QoSReliabilityPolicy
from turtlesim_msgs.msg import Pose
from turtlesim_msgs.srv import TeleportAbsolute

NS = f'/follow_test_{os.getpid()}'
SENSOR_POSE = f'{NS}/sensor_pose'
TELEPORT = f'{NS}/teleport_absolute'


def pose(x=1.0, y=2.0, theta=0.5):
    msg = Pose()
    msg.x, msg.y, msg.theta = x, y, theta
    return msg


def init(*extra):
    # The turtle service is remapped away from /turtle1, so the tests can never
    # move a live turtlesim on the same ROS_DOMAIN_ID.
    rclpy.init(args=['--ros-args', '-r', f'__ns:={NS}',
                     '-r', f'/turtle1/teleport_absolute:={TELEPORT}', *extra])


def spin_until(nodes, condition, seconds=25.0):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline and not condition():
        for node in nodes:
            rclpy.spin_once(node, timeout_sec=0.05)
    return condition()


@pytest.fixture
def shutdown():
    yield
    rclpy.try_shutdown()


def test_nothing_to_send_before_the_first_pose():
    assert pose_changed(None, None) is False


def test_first_pose_is_sent():
    assert pose_changed(None, pose()) is True


def test_same_pose_is_not_sent_again():
    assert pose_changed(pose(), pose()) is False


@pytest.mark.parametrize('moved', [pose(x=1.5), pose(y=2.5), pose(theta=1.0)])
def test_any_change_of_x_y_or_theta_is_sent(moved):
    assert pose_changed(pose(), moved) is True


def test_subscription_is_best_effort_on_a_relative_topic(shutdown):
    init()
    follower = PoseFollower()
    assert follower._sub.topic_name == SENSOR_POSE
    assert follower._sub.qos_profile.reliability == QoSReliabilityPolicy.BEST_EFFORT
    follower.destroy_node()


def test_bad_rate_is_rejected(shutdown):
    init('-p', 'rate_hz:=0.0')
    with pytest.raises(ValueError):
        PoseFollower()


def test_turtle_is_asked_to_go_to_the_published_pose(shutdown):
    init()
    received = []

    def teleport(request, response):
        received.append((request.x, request.y, request.theta))
        return response

    server = rclpy.create_node('fake_turtle')
    server.create_service(TeleportAbsolute, TELEPORT, teleport)
    source = rclpy.create_node('fake_sensor')
    publisher = source.create_publisher(Pose, SENSOR_POSE, 10)
    follower = PoseFollower()
    # Only the nodes that have callbacks are spun; the source just publishes.
    nodes = [server, follower]

    def publish_and_check():
        publisher.publish(pose(3.0, 4.0, 1.25))
        return bool(received)

    assert spin_until(nodes, publish_and_check)
    assert received[0] == pytest.approx((3.0, 4.0, 1.25))
    for node in nodes + [source]:
        node.destroy_node()
