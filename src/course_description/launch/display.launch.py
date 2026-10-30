from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    share = FindPackageShare('course_description')
    model = LaunchConfiguration('model')
    rviz = LaunchConfiguration('rviz')

    return LaunchDescription([
        DeclareLaunchArgument(
            'model',
            default_value=PathJoinSubstitution([share, 'urdf', 'vehicle.urdf.xacro']),
            description='Path of the .urdf.xacro model to publish'),
        DeclareLaunchArgument(
            'rviz', default_value='false',
            description='true: also open RViz with the robot model and the tf tree'),

        # The single owner of /tf_static (fixed links) and of /tf for joints
        # whose positions arrive on /joint_states.
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{
                'robot_description': ParameterValue(Command(['xacro ', model]), value_type=str),
            }],
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', PathJoinSubstitution([share, 'rviz', 'vehicle.rviz'])],
            condition=IfCondition(rviz),
            output='screen',
        ),
    ])
