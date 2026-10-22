import importlib.util
from pathlib import Path

from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch_ros.actions import Node

LAUNCH_FILE = Path(__file__).resolve().parent.parent / 'launch' / 'patrol.launch.py'


def load_entities():
    spec = importlib.util.spec_from_file_location('patrol_launch', LAUNCH_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_launch_description().entities


def test_declares_the_four_arguments_with_defaults():
    arguments = {
        entity.name: entity
        for entity in load_entities() if isinstance(entity, DeclareLaunchArgument)}
    assert set(arguments) == {'namespace', 'record', 'bag_dir', 'subscriber_reliability'}
    assert arguments['record'].default_value[0].text == 'false'
    assert arguments['namespace'].default_value[0].text == 'robot_a'


def test_recorder_is_started_through_if_condition():
    recorders = [
        e for e in load_entities()
        if isinstance(e, ExecuteProcess) and not isinstance(e, Node)]
    assert len(recorders) == 1
    assert isinstance(recorders[0].condition, IfCondition)


def test_launches_turtlesim_and_the_three_robot_nodes():
    nodes = [e for e in load_entities() if isinstance(e, Node)]
    executables = {node.node_executable for node in nodes}
    assert executables == {'turtlesim_node', 'patrol', 'pose_relay', 'sensor_listener'}
