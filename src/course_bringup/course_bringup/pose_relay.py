from course_bringup.qos import make_qos
from course_bringup.runner import run
from rclpy.node import Node
from turtlesim_msgs.msg import Pose

INPUT_TOPIC = '/turtle1/pose'
OUTPUT_TOPIC = 'sensor_pose'


class PoseRelay(Node):
    """Republish the turtle pose as a best-effort 'sensor' stream."""

    def __init__(self):
        super().__init__('pose_relay')
        self._pub = self.create_publisher(Pose, OUTPUT_TOPIC, make_qos('best_effort'))
        self._sub = self.create_subscription(Pose, INPUT_TOPIC, self._on_pose, 10)

    def _on_pose(self, msg):
        self._pub.publish(msg)


def main(args=None):
    run(PoseRelay, args)


if __name__ == '__main__':
    main()
