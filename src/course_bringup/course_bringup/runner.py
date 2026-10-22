import rclpy
from rclpy.executors import ExternalShutdownException


def run(node_class, args=None):
    """Init rclpy, spin one node until shutdown, then clean up."""
    rclpy.init(args=args)
    node = node_class()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    except Exception:
        # After Ctrl+C / launch shutdown the context is already gone and
        # spin() may fail on that race. Anything else is a real error.
        if rclpy.ok():
            raise
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
