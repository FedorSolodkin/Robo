import time

from course_bringup.qos import make_qos
from course_bringup.runner import run
from rclpy.node import Node
from turtlesim_msgs.msg import Pose
from turtlesim_msgs.srv import TeleportAbsolute

INPUT_TOPIC = 'sensor_pose'
TELEPORT_SERVICE = '/turtle1/teleport_absolute'
MIN_STEP = 1e-3
REQUEST_TIMEOUT = 1.0
READY_GRACE = 1.0


def pose_changed(previous, current, eps=MIN_STEP):
    """Return True when `current` is a new pose worth sending to the turtle."""
    if current is None:
        return False
    if previous is None:
        return True
    return (abs(current.x - previous.x) > eps
            or abs(current.y - previous.y) > eps
            or abs(current.theta - previous.theta) > eps)


class PoseFollower(Node):
    """Put the turtle at every pose that arrives on sensor_pose (live or replayed)."""

    def __init__(self):
        super().__init__('pose_follower')
        self.declare_parameter('reliability', 'best_effort')
        self.declare_parameter('rate_hz', 20.0)
        reliability = self.get_parameter('reliability').value
        rate_hz = self.get_parameter('rate_hz').value
        if not isinstance(rate_hz, float) or not 1.0 <= rate_hz <= 60.0:
            raise ValueError('rate_hz must be a number within [1.0, 60.0]')

        self.sent_count = 0
        self.lost_requests = 0
        self._latest = None
        self._sent = None
        self._pending = False
        self._pending_since = 0.0
        self._ready_since = None
        self._client = self.create_client(TeleportAbsolute, TELEPORT_SERVICE)
        self._sub = self.create_subscription(
            Pose, INPUT_TOPIC, self._on_pose, make_qos(reliability))
        self._timer = self.create_timer(1.0 / rate_hz, self._on_timer)
        self.get_logger().info(
            f'following {self._sub.topic_name} with reliability={reliability} '
            f'at most {rate_hz:g} times per second')

    def _on_pose(self, msg):
        self._latest = msg

    def _on_timer(self):
        # One teleport request at a time: a slow turtle must not build a queue.
        # A request can be lost while the service connection is still being set
        # up, so a pending one is given up after REQUEST_TIMEOUT seconds.
        if self._pending and time.monotonic() - self._pending_since > REQUEST_TIMEOUT:
            self._pending = False
            self.lost_requests += 1
            self._sent = None
        if not self._client.service_is_ready():
            self._ready_since = None
            return
        # A request sent in the first moments after discovery can be dropped,
        # so wait READY_GRACE seconds once the service has appeared.
        if self._ready_since is None:
            self._ready_since = time.monotonic()
        if self._pending or time.monotonic() - self._ready_since < READY_GRACE:
            return
        if not pose_changed(self._sent, self._latest):
            return
        request = TeleportAbsolute.Request()
        request.x = self._latest.x
        request.y = self._latest.y
        request.theta = self._latest.theta
        self._sent = self._latest
        self._pending = True
        self._pending_since = time.monotonic()
        self._client.call_async(request).add_done_callback(self._on_done)

    def _on_done(self, future):
        self._pending = False
        self.sent_count += 1


def main(args=None):
    run(PoseFollower, args)


if __name__ == '__main__':
    main()
