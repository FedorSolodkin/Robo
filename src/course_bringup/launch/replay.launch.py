from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, LogInfo
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    bag = LaunchConfiguration('bag')
    qos_overrides = LaunchConfiguration('qos_overrides')
    delay = LaunchConfiguration('delay')
    loop = LaunchConfiguration('loop')

    play = ['ros2', 'bag', 'play', bag, '--qos-profile-overrides-path', qos_overrides,
            '--delay', delay]

    return LaunchDescription([
        DeclareLaunchArgument(
            'bag', description='Recorded MCAP bag with /<namespace>/sensor_pose'),
        DeclareLaunchArgument(
            'namespace', default_value='robot_a',
            description='Namespace the pose was recorded in'),
        DeclareLaunchArgument(
            'qos_overrides', default_value='config/qos-overrides.yaml',
            description='QoS profile of the replayed topic (path relative to where you launch)'),
        DeclareLaunchArgument(
            'delay', default_value='8',
            description='Seconds to wait before playing, so the nodes are ready'),
        DeclareLaunchArgument(
            'loop', default_value='true',
            description='true: play the recording again and again'),

        LogInfo(msg=['Replaying ', bag, ' into /', namespace,
                     '/sensor_pose: the turtle follows the recorded poses']),

        # The same global simulator as in the live system.
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),
        # Moves the turtle to every replayed pose.
        Node(
            package='course_bringup',
            executable='pose_follower',
            namespace=namespace,
            output='screen',
        ),
        ExecuteProcess(cmd=play + ['--loop'], condition=IfCondition(loop), output='screen'),
        ExecuteProcess(cmd=play, condition=UnlessCondition(loop), output='screen'),
    ])
