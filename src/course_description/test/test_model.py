from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from course_description.urdf_tree import (
    expand, link_names, main, pose_in, read_joints, structure_errors)
import pytest

MODEL = Path(__file__).resolve().parent.parent / 'urdf' / 'vehicle.urdf.xacro'

# Parent of every link: the contract of the model.
EXPECTED_PARENTS = {
    'front_left_knuckle': 'base_link',
    'front_right_knuckle': 'base_link',
    'front_left_wheel': 'front_left_knuckle',
    'front_right_wheel': 'front_right_knuckle',
    'rear_left_wheel': 'base_link',
    'rear_right_wheel': 'base_link',
    'camera_link': 'base_link',
    'lidar_link': 'base_link',
    'imu_link': 'base_link',
}

# Positions in base_link, metres (sizes of models/course_ackermann/model.sdf).
EXPECTED_POSITIONS = {
    'front_left_wheel': (0.4, 0.31, 0.0),
    'front_right_wheel': (0.4, -0.31, 0.0),
    'rear_left_wheel': (-0.4, 0.31, 0.0),
    'rear_right_wheel': (-0.4, -0.31, 0.0),
    'camera_link': (0.28, 0.0, 0.38),
    'lidar_link': (0.28, 0.0, 0.38),
    'imu_link': (0.28, 0.0, 0.38),
}


@pytest.fixture(scope='module')
def robot():
    return expand(MODEL)


@pytest.fixture(scope='module')
def joints(robot):
    return read_joints(robot)


def test_xacro_expands_to_a_robot(robot):
    assert robot.tag == 'robot'
    assert robot.get('name') == 'course_ackermann'
    assert len(link_names(robot)) == 10


def test_tree_is_connected_acyclic_and_rooted_at_base_link(robot):
    assert structure_errors(robot) == []


def test_every_link_has_the_expected_parent(joints):
    parents = {child: joint.parent for child, joint in joints.items()}
    assert parents == EXPECTED_PARENTS


@pytest.mark.parametrize('frame', sorted(EXPECTED_POSITIONS))
def test_frame_position_in_base_link(joints, frame):
    assert pose_in(joints, frame) == pytest.approx(EXPECTED_POSITIONS[frame], abs=1e-9)


def test_joint_types_axes_and_limits(joints):
    for name in ('front_left_wheel', 'front_right_wheel', 'rear_left_wheel', 'rear_right_wheel'):
        assert joints[name].kind == 'continuous'
        assert joints[name].axis == (0.0, 1.0, 0.0)
    for name in ('front_left_knuckle', 'front_right_knuckle'):
        joint = joints[name]
        assert joint.kind == 'revolute'
        assert joint.axis == (0.0, 0.0, 1.0)
        assert float(joint.limit['lower']) == pytest.approx(-0.55)
        assert float(joint.limit['upper']) == pytest.approx(0.55)
    for name in ('camera_link', 'lidar_link', 'imu_link'):
        assert joints[name].kind == 'fixed'


def test_geometry_parameters_are_xacro_arguments():
    custom = read_joints(expand(
        MODEL, {'wheel_base': '1.0', 'track_width': '0.7', 'wheel_radius': '0.15'}))
    assert pose_in(custom, 'front_left_wheel') == pytest.approx((0.5, 0.35, 0.0))
    assert pose_in(custom, 'rear_right_wheel') == pytest.approx((-0.5, -0.35, 0.0))
    robot = expand(MODEL, {'wheel_radius': '0.15'})
    cylinder = robot.find("link[@name='rear_left_wheel']/visual/geometry/cylinder")
    assert float(cylinder.get('radius')) == pytest.approx(0.15)


def test_visual_and_collision_are_separate_elements(robot):
    for name in ('base_link', 'front_left_wheel', 'front_right_wheel',
                 'rear_left_wheel', 'rear_right_wheel'):
        link = robot.find(f"link[@name='{name}']")
        assert link.find('visual') is not None
        assert link.find('collision') is not None
        assert link.find('visual') is not link.find('collision')


def test_inertia_is_physically_possible(robot):
    for link in robot.findall('link'):
        inertial = link.find('inertial')
        assert inertial is not None, link.get('name')
        mass = float(inertial.find('mass').get('value'))
        assert mass > 0.0
        inertia = inertial.find('inertia')
        ixx, iyy, izz = (float(inertia.get(key)) for key in ('ixx', 'iyy', 'izz'))
        assert min(ixx, iyy, izz) > 0.0
        # Principal moments of a real body obey the triangle inequality.
        assert ixx + iyy >= izz - 1e-12
        assert ixx + izz >= iyy - 1e-12
        assert iyy + izz >= ixx - 1e-12


def test_numbers_are_in_si_units(robot):
    masses = [float(m.get('value')) for m in robot.iter('mass')]
    assert max(masses) < 100.0
    for box in robot.iter('box'):
        assert all(0.0 < float(side) < 5.0 for side in box.get('size').split())
    for cylinder in robot.iter('cylinder'):
        assert 0.0 < float(cylinder.get('radius')) < 1.0


@pytest.mark.skipif(shutil.which('check_urdf') is None, reason='check_urdf is not installed')
def test_check_urdf_accepts_the_expanded_model(robot, tmp_path):
    urdf = tmp_path / 'vehicle.urdf'
    urdf.write_text(ET.tostring(robot, encoding='unicode'))
    result = subprocess.run(['check_urdf', str(urdf)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'robot name is: course_ackermann' in result.stdout


def test_frames_report_command_succeeds(capsys):
    assert main([str(MODEL)]) == 0
    assert 'structure: OK' in capsys.readouterr().out
