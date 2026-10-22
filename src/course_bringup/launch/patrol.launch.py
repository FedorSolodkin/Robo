from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')

    # '/robot_a/sensor_pose' whatever way the namespace was written.
    sensor_topic = PythonExpression(
        ["'/' + '", namespace, "'.strip('/') + '/sensor_pose'"])

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace', default_value='robot_a',
            description='Namespace of the whole robot system'),
        DeclareLaunchArgument(
            'record', default_value='false',
            description='true: also start ros2 bag record (MCAP) for sensor_pose'),
        DeclareLaunchArgument(
            'bag_dir', default_value='bags/robot_a',
            description='Output directory of the recording (must not exist yet)'),
        DeclareLaunchArgument(
            'subscriber_reliability', default_value='best_effort',
            description='QoS reliability of the sensor_listener: reliable or best_effort'),

        LogInfo(msg=['Starting the system in namespace /', namespace,
                     ' (listener reliability: ', subscriber_reliability,
                     ', record: ', record, ')']),

        # One simulator for everybody: global, outside the robot namespace.
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),
        # Relative topic names inside the node; the remap points its command
        # output at the one global turtle.
        Node(
            package='patrol',
            executable='patrol',
            namespace=namespace,
            remappings=[('cmd_vel', '/turtle1/cmd_vel')],
            output='screen',
        ),
        Node(
            package='course_bringup',
            executable='pose_relay',
            namespace=namespace,
            output='screen',
        ),
        Node(
            package='course_bringup',
            executable='sensor_listener',
            namespace=namespace,
            parameters=[{
                'reliability': ParameterValue(subscriber_reliability, value_type=str),
            }],
            output='screen',
        ),
        # IfCondition on the substitution: LaunchConfiguration is not a bool
        # at description time, so a plain `if` would always be truthy.
        ExecuteProcess(
            cmd=['ros2', 'bag', 'record', '-s', 'mcap', '-o', bag_dir,
                 '--topics', sensor_topic],
            condition=IfCondition(record),
            output='screen',
        ),
    ])
