from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy

SENSOR_DEPTH = 10

RELIABILITY = {
    'reliable': QoSReliabilityPolicy.RELIABLE,
    'best_effort': QoSReliabilityPolicy.BEST_EFFORT,
}


def parse_reliability(name):
    """Turn 'reliable' / 'best_effort' into a reliability policy."""
    if not isinstance(name, str) or name not in RELIABILITY:
        allowed = ', '.join(sorted(RELIABILITY))
        raise ValueError(f'reliability must be one of: {allowed} (got {name!r})')
    return RELIABILITY[name]


def make_qos(reliability):
    """Build the profile used on /<ns>/sensor_pose: keep_last, depth 10."""
    return QoSProfile(
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=SENSOR_DEPTH,
        reliability=parse_reliability(reliability))
