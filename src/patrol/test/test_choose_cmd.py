from patrol.patrol import choose_cmd
from turtlesim_msgs.msg import Pose


def test_no_pose_gives_zero_command_whatever_the_params():
    assert choose_cmd(None, 0.9, -0.7) == (0.0, 0.0)


def test_pose_gives_configured_command():
    assert choose_cmd(Pose(), 0.5, 0.3) == (0.5, 0.3)


def test_command_follows_changed_params():
    assert choose_cmd(Pose(), 1.0, -1.0) == (1.0, -1.0)
