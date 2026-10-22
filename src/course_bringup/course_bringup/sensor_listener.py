from course_bringup.qos import make_qos
from course_bringup.runner import run
from rclpy.event_handler import SubscriptionEventCallbacks
from rclpy.node import Node
from turtlesim_msgs.msg import Pose

INPUT_TOPIC = 'sensor_pose'


class SensorListener(Node):
    """Subscribe to sensor_pose with a reliability chosen by a parameter."""

    def __init__(self):
        super().__init__('sensor_listener')
        self.declare_parameter('reliability', 'reliable')
        reliability = self.get_parameter('reliability').value
        self.received = 0
        self.incompatible_events = 0
        self._sub = self.create_subscription(
            Pose, INPUT_TOPIC, self._on_pose, make_qos(reliability),
            event_callbacks=SubscriptionEventCallbacks(
                incompatible_qos=self._on_incompatible_qos))
        self.get_logger().info(
            f'listening on {self._sub.topic_name} with reliability={reliability}')

    def _on_incompatible_qos(self, event):
        self.incompatible_events = event.total_count
        self.get_logger().warning(
            f'incompatible QoS on {self._sub.topic_name}: '
            f'total_count={event.total_count}, last_policy_kind={event.last_policy_kind}')

    def _on_pose(self, msg):
        self.received += 1
        self.get_logger().info(
            f'received #{self.received}: x={msg.x:.2f} y={msg.y:.2f}',
            throttle_duration_sec=2.0)


def main(args=None):
    run(SensorListener, args)


if __name__ == '__main__':
    main()
