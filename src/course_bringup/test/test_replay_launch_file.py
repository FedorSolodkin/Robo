import importlib.util
from pathlib import Path

from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node

LAUNCH_FILE = Path(__file__).resolve().parent.parent / 'launch' / 'replay.launch.py'


def load_entities():
    spec = importlib.util.spec_from_file_location('replay_launch', LAUNCH_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_launch_description().entities


def test_declares_the_replay_arguments():
    arguments = {
        entity.name: entity
        for entity in load_entities() if isinstance(entity, DeclareLaunchArgument)}
    assert set(arguments) == {'bag', 'namespace', 'qos_overrides', 'delay', 'loop'}
    assert arguments['loop'].default_value[0].text == 'true'
    assert arguments['namespace'].default_value[0].text == 'robot_a'


def test_starts_turtlesim_and_the_follower_only():
    nodes = [e for e in load_entities() if isinstance(e, Node)]
    assert {node.node_executable for node in nodes} == {'turtlesim_node', 'pose_follower'}


def test_player_runs_once_or_in_a_loop_depending_on_the_argument():
    players = [
        e for e in load_entities()
        if isinstance(e, ExecuteProcess) and not isinstance(e, Node)]
    assert len(players) == 2
    conditions = {type(player.condition) for player in players}
    assert conditions == {IfCondition, UnlessCondition}
