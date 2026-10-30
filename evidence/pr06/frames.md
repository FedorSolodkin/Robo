# Системы координат модели course_ackermann (ПР06)

Единицы СИ: метры, радианы. Оси по REP-103: x вперёд, y влево, z вверх.
Корень дерева: `base_link` (середина продольной оси колёс, на уровне осей). Положения даны в
`base_link` при нулевых положениях сочленений. Размеры взяты из `models/course_ackermann/model.sdf`
курса; значения геометрии параметризованы в `vehicle.urdf.xacro` (`wheel_base`, `track_width`,
`wheel_radius`).

## Связи дерева

| Родитель | Потомок | Сочленение | Тип | Смещение parent→child, м | Ось | Канал | Владелец публикации |
|---|---|---|---|---|---|---|---|
| `base_link` | `camera_link` | `camera_joint` | fixed | (0.28, 0, 0.38) | — | `/tf_static` | `robot_state_publisher` |
| `base_link` | `lidar_link` | `lidar_joint` | fixed | (0.28, 0, 0.38) | — | `/tf_static` | `robot_state_publisher` |
| `base_link` | `imu_link` | `imu_joint` | fixed | (0.28, 0, 0.38) | — | `/tf_static` | `robot_state_publisher` |
| `base_link` | `front_left_knuckle` | `front_left_steering_joint` | revolute ±0.55 рад | (0.40, 0.31, 0) | z | `/tf` | `robot_state_publisher` (нужен `/joint_states`) |
| `base_link` | `front_right_knuckle` | `front_right_steering_joint` | revolute ±0.55 рад | (0.40, −0.31, 0) | z | `/tf` | `robot_state_publisher` (нужен `/joint_states`) |
| `front_left_knuckle` | `front_left_wheel` | `front_left_wheel_joint` | continuous | (0, 0, 0) | y | `/tf` | `robot_state_publisher` (нужен `/joint_states`) |
| `front_right_knuckle` | `front_right_wheel` | `front_right_wheel_joint` | continuous | (0, 0, 0) | y | `/tf` | `robot_state_publisher` (нужен `/joint_states`) |
| `base_link` | `rear_left_wheel` | `rear_left_wheel_joint` | continuous | (−0.40, 0.31, 0) | y | `/tf` | `robot_state_publisher` (нужен `/joint_states`) |
| `base_link` | `rear_right_wheel` | `rear_right_wheel_joint` | continuous | (−0.40, −0.31, 0) | y | `/tf` | `robot_state_publisher` (нужен `/joint_states`) |

Вращения у всех смещений нулевые (rpy = 0 0 0). Положение колёс в `base_link`: передние
(±0.40, ±0.31, 0) через поворотные кулаки при нулевом угле, задние напрямую.

## Владельцы

- **Одна нода публикует всё дерево:** `/robot_state_publisher`. Это подтверждают
  `ros2 topic info /tf_static --verbose` и `ros2 topic info /tf --verbose`:
  по одному издателю, `robot_state_publisher` ([fixed-owners.txt](fixed-owners.txt),
  [tf-qos.txt](tf-qos.txt)).
- **`/tf_static`** (камера, лидар, IMU): профиль RELIABLE + TRANSIENT_LOCAL, глубина 1. Поздний
  подписчик получает три преобразования сразу.
- **`/tf`** (колёса и кулаки): без `/joint_states` этих звеньев в дереве нет. В обязательной части
  `/joint_states` никто не публикует. Для показа полного дерева положения опубликованы вручную
  командой `ros2 topic pub -r 10 /joint_states …`; владелец самих преобразований остаётся
  прежним ([good-joint-states.txt](good-joint-states.txt)).
- **`map`, `odom`** не публикуются: в RViz Fixed Frame = `base_link`.
- Перед повторным запуском прежний launch останавливается: два издателя `/tf_static` дают
  случайный ответ.

## Что неверно при дефекте

Если `lidar_link` сделать потомком `camera_link` (а не `base_link`) при том же смещении,
смещения складываются: лидар оказывается в (0.56, 0, 0.76) вместо (0.28, 0, 0.38). `check_urdf`
и проверка структуры такое дерево принимают (оно связное и ациклическое); неверное положение
находят только проверки ожидаемого родителя и положения
([defect-tests.txt](defect-tests.txt), [defect-tf2-echo-lidar.txt](defect-tf2-echo-lidar.txt)).
