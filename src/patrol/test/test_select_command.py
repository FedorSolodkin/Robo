from turtlesim_msgs.msg import Pose

from patrol.patrol import select_command


def test_select_command_without_pose_is_zero():
    linear_x, angular_z = select_command(None)
    assert linear_x == 0.0
    assert angular_z == 0.0


def test_select_command_with_pose_is_fixed_forward_turn():
    pose = Pose()
    pose.x = 5.0
    pose.y = 5.0
    pose.theta = 0.0
    linear_x, angular_z = select_command(pose)
    assert linear_x == 0.5
    assert angular_z == 0.3
