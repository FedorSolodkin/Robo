import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim_msgs.msg import Pose

FORWARD_LINEAR_X = 0.5
FORWARD_ANGULAR_Z = 0.3


def select_command(last_pose):
    """Pure function: last known pose (or None) -> (linear.x, angular.z).

    No pose received yet -> stay still. Once a pose arrives, patrol at a
    fixed forward-and-turn velocity. Kept pure (no ROS types in, no ROS
    types out) so it can be unit-tested without rclpy.init().
    """
    if last_pose is None:
        return 0.0, 0.0
    return FORWARD_LINEAR_X, FORWARD_ANGULAR_Z


class PatrolNode(Node):

    def __init__(self):
        super().__init__('patrol')
        self._last_pose = None
        self._pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self._on_pose, 10)
        self._cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self._timer = self.create_timer(0.1, self._on_timer)

    def _on_pose(self, msg):
        self._last_pose = msg

    def _on_timer(self):
        linear_x, angular_z = select_command(self._last_pose)
        twist = Twist()
        twist.linear.x = linear_x
        twist.angular.z = angular_z
        self._cmd_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
