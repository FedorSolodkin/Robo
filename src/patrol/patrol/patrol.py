import math

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from turtlesim_msgs.msg import Pose

DEFAULT_LINEAR_SPEED = 0.5
DEFAULT_TURN_RATE = 0.3
DEFAULT_PUBLISH_HZ = 10.0

PARAM_RANGES = {
    'linear_speed': (0.0, 1.0),
    'turn_rate': (-1.0, 1.0),
    'publish_hz': (1.0, 30.0),
}


def choose_cmd(last_pose, linear_speed, turn_rate):
    """Return (linear.x, angular.z): zero until the first pose arrives."""
    if last_pose is None:
        return 0.0, 0.0
    return linear_speed, turn_rate


def validate_param(name, value):
    """Check one parameter value and return (ok, reason)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False, f'{name} must be a number'
    if not math.isfinite(value):
        return False, f'{name} must be finite'
    low, high = PARAM_RANGES[name]
    if not low <= value <= high:
        return False, f'{name} must be within [{low}, {high}]'
    return True, ''


class PatrolNode(Node):

    def __init__(self):
        super().__init__('patrol')
        self.declare_parameter('linear_speed', DEFAULT_LINEAR_SPEED)
        self.declare_parameter('turn_rate', DEFAULT_TURN_RATE)
        self.declare_parameter('publish_hz', DEFAULT_PUBLISH_HZ)
        for name in PARAM_RANGES:
            ok, reason = validate_param(name, self.get_parameter(name).value)
            if not ok:
                raise ValueError(reason)

        self._last_pose = None
        self._pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self._on_pose, 10)
        self._cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self._timer = self.create_timer(
            1.0 / self.get_parameter('publish_hz').value, self._on_timer)

        self.add_on_set_parameters_callback(self._on_set_parameters)

    def _on_pose(self, msg):
        self._last_pose = msg

    def _on_set_parameters(self, params):
        for param in params:
            if param.name in PARAM_RANGES:
                ok, reason = validate_param(param.name, param.value)
                if not ok:
                    return SetParametersResult(successful=False, reason=reason)
        for param in params:
            if param.name == 'publish_hz':
                self._restart_timer(param.value)
        return SetParametersResult(successful=True)

    def _restart_timer(self, hz):
        new_timer = self.create_timer(1.0 / hz, self._on_timer)
        old_timer = self._timer
        self._timer = new_timer
        self.destroy_timer(old_timer)

    def _on_timer(self):
        linear_x, angular_z = choose_cmd(
            self._last_pose,
            self.get_parameter('linear_speed').value,
            self.get_parameter('turn_rate').value)
        twist = Twist()
        twist.linear.x = linear_x
        twist.angular.z = angular_z
        self._cmd_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    except Exception:
        # After Ctrl+C the context is already shut down; spin() may fail
        # on that race, which is expected. Anything else is a real error.
        if rclpy.ok():
            raise
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
