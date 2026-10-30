"""Read the expanded robot model: joint tree, frame poses and structural errors."""
import math
from pathlib import Path
import sys
from typing import NamedTuple
import xml.etree.ElementTree as ET

import xacro

DEFAULT_MODEL = Path(__file__).resolve().parent.parent / 'urdf' / 'vehicle.urdf.xacro'


class Joint(NamedTuple):
    name: str
    kind: str
    parent: str
    child: str
    xyz: tuple
    rpy: tuple
    axis: tuple
    limit: dict


def expand(path, mappings=None):
    """Expand a .urdf.xacro file (like the `xacro` command) and return the XML root."""
    document = xacro.process_file(str(path), mappings=mappings or {})
    return ET.fromstring(document.toxml())


def _floats(text, default):
    return tuple(float(value) for value in (text or default).split())


def read_joints(root):
    """Return {child link name: Joint}; a child that appears twice keeps the last joint."""
    joints = {}
    for element in root.findall('joint'):
        origin = element.find('origin')
        axis = element.find('axis')
        limit = element.find('limit')
        joint = Joint(
            name=element.get('name'),
            kind=element.get('type'),
            parent=element.find('parent').get('link'),
            child=element.find('child').get('link'),
            xyz=_floats(origin.get('xyz') if origin is not None else None, '0 0 0'),
            rpy=_floats(origin.get('rpy') if origin is not None else None, '0 0 0'),
            axis=_floats(axis.get('xyz') if axis is not None else None, '1 0 0'),
            limit=dict(limit.attrib) if limit is not None else {})
        joints[joint.child] = joint
    return joints


def link_names(root):
    return [link.get('name') for link in root.findall('link')]


def structure_errors(root, base='base_link'):
    """List why the joint tree is not a single connected tree rooted at `base`."""
    errors = []
    links = link_names(root)
    children = [joint.get('name') for joint in root.findall('joint')]
    if len(set(links)) != len(links):
        errors.append('duplicate link names')
    if len(set(children)) != len(children):
        errors.append('duplicate joint names')
    seen_children = [j.find('child').get('link') for j in root.findall('joint')]
    for name in set(seen_children):
        if seen_children.count(name) > 1:
            errors.append(f'link {name} has more than one parent joint')
    joints = read_joints(root)
    for child, joint in joints.items():
        if joint.parent not in links or child not in links:
            errors.append(f'joint {joint.name} refers to an unknown link')
    roots = [name for name in links if name not in joints]
    if roots != [base]:
        errors.append(f'expected the only root {base}, found {roots}')
    for name in links:
        walked = set()
        current = name
        while current in joints:
            if current in walked:
                errors.append(f'cycle through {current}')
                break
            walked.add(current)
            current = joints[current].parent
        else:
            if current != base and roots == [base]:
                errors.append(f'{name} is not connected to {base}')
    return errors


def _rotation(rpy):
    roll, pitch, yaw = rpy
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return [
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr]]


def _multiply(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(3)) for j in range(3)]
            for i in range(3)]


def pose_in(joints, frame, ancestor='base_link'):
    """Return `frame` position in `ancestor` by composing joint origins (joint angles 0)."""
    chain = []
    current = frame
    while current != ancestor:
        joint = joints[current]
        chain.append(joint)
        current = joint.parent
    rotation = [[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]]
    translation = [0.0, 0.0, 0.0]
    for joint in reversed(chain):
        for i in range(3):
            translation[i] += sum(rotation[i][k] * joint.xyz[k] for k in range(3))
        rotation = _multiply(rotation, _rotation(joint.rpy))
    return tuple(round(value, 9) for value in translation)


def report(root):
    """Text table: every link with its parent joint and its position in base_link."""
    joints = read_joints(root)
    lines = ['link               parent             joint type   x       y       z']
    for name in link_names(root):
        if name in joints:
            joint = joints[name]
            x, y, z = pose_in(joints, name)
            lines.append(
                f'{name:<18} {joint.parent:<18} {joint.kind:<11} {x:7.3f} {y:7.3f} {z:7.3f}')
        else:
            lines.append(f'{name:<18} {"(root)":<18} {"-":<11} {0:7.3f} {0:7.3f} {0:7.3f}')
    return '\n'.join(lines)


def main(args=None):
    argv = sys.argv[1:] if args is None else args
    path = argv[0] if argv else DEFAULT_MODEL
    root = expand(path)
    print(report(root))
    errors = structure_errors(root)
    print('structure: ' + ('OK (single connected tree rooted at base_link)' if not errors
                           else '; '.join(errors)))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
