# ПР06 — всё по этой задаче в одном месте

- **Код:** [../../src/course_description/](../../src/course_description/) — модель
  [`urdf/vehicle.urdf.xacro`](../../src/course_description/urdf/vehicle.urdf.xacro), запуск
  [`launch/display.launch.py`](../../src/course_description/launch/display.launch.py), команда
  `frames_report`, тесты
- **Отчёт для проверки:** [report.json](report.json)
- **Таблица систем координат и владельцев:** [frames.md](frames.md)
- **Декларация ИИ:** [../../AI_USAGE.md](../../AI_USAGE.md) (раздел «ПР06»)
- **Коммит реализации** (`report.commit`): `b5e71f945e0dcbc4655036899434d3539dbb8c18`
- **Дефектный коммит** (стадия «Сломать», ветка `defect/pr06-lidar-parent`):
  `8eb7c525c9d680fe8cf23cab9b44f38a4f31b39a` — красный CI:
  [actions/runs/41011891857](https://github.com/FedorSolodkin/Robo/actions/runs/41011891857)

## Что устроено

`vehicle.urdf.xacro` описывает Ackermann-робота `course_ackermann` по размерам из SDF курса
(метры, килограммы, радианы, оси по REP-103). Параметры `wheel_base`, `track_width` и
`wheel_radius` — аргументы Xacro, а не магические числа. Звенья: `base_link`, два поворотных
кулака, четыре колеса (непрерывные сочленения), `camera_link`, `lidar_link`, `imu_link`
(фиксированные сочленения). Визуальная геометрия, геометрия столкновений и инерция заданы
отдельно. Все фиксированные звенья крепятся к `base_link` со смещением (0.28; 0; 0.38).

`robot_state_publisher` — единственный издатель `/tf_static` и `/tf`.

## Как повторить

```bash
docker exec -it pr01-submission bash
cd /work && source install/setup.bash

xacro src/course_description/urdf/vehicle.urdf.xacro > /tmp/vehicle.urdf && check_urdf /tmp/vehicle.urdf
ros2 run course_description frames_report           # дерево и положения в base_link
colcon test --packages-select course_description    # или: python3 -m pytest src/course_description/test

ros2 launch course_description display.launch.py                  # терминал A
ros2 run tf2_ros tf2_echo base_link lidar_link                    # B: [0.280, 0.000, 0.380]
timeout 30 ros2 topic echo /tf_static --once --qos-durability transient_local --qos-reliability reliable   # три преобразования
timeout 30 ros2 topic echo /tf_static --once --qos-durability volatile --qos-reliability reliable          # пусто, exit=124
```

## Файлы показаний

| Файл | Что в нём |
|---|---|
| [tf-qos.txt](tf-qos.txt) | профиль `/tf_static`, поздний подписчик с transient local и volatile, пояснение |
| [frames.md](frames.md) | родитель, потомок, преобразование и владелец каждой связи |
| [model-check.txt](model-check.txt) | `xacro`, `check_urdf`, `frames_report`, `colcon test` исправной модели |
| `good-*`, `fixed-*` | исправная модель: `tf2_echo`, `view_frames`, статические преобразования, владельцы `/tf` и `/tf_static`, дерево с `joint_states` |
| `defect-model-check.txt`, `defect-tests.txt`, `defect-tf2-echo-lidar.txt`, `defect-view-frames.gv` | дефект: `check_urdf` и структура в порядке, 2 теста красные, лидар в (0.56; 0; 0.76) |
| [fixed-tests.txt](fixed-tests.txt) | те же тесты после возврата родителя: 21 passed |
| [rviz-launch.txt](rviz-launch.txt) | попытка открыть модель в RViz (см. ограничения) |

## Ограничения и находки, записанные как есть

- **RViz не открылся.** В контейнере (эмуляция amd64 и XQuartz) `rviz2` падает при создании
  OpenGL-окна: `No matching fbConfigs or visuals found`, затем segmentation fault; режимы
  программной отрисовки не помогли. Launch-файл и конфигурация RViz
  ([rviz/vehicle.rviz](../../src/course_description/rviz/vehicle.rviz)) готовы
  (`rviz:=true`), но показ в RViz не подтверждён. Корректность модели доказана `check_urdf`,
  тестами, `tf2_echo` и `view_frames`.
- `robot_state_publisher` предупреждает, что у корня `base_link` задана инерция, а KDL её не
  поддерживает. Это предупреждение не влияет на tf; корень оставлен `base_link` по условию.
- Предел скорости поворота кулака (`velocity="2.0"` рад/с) в SDF отсутствует и взят как допущение.
- Таймауты `ros2 topic echo` подняты с 4 до 30 секунд: контейнер идёт под эмуляцией amd64.
- Колёса и кулаки появляются в `/tf` только при наличии `/joint_states`; в обязательной части
  их никто не публикует, поэтому показано отдельным опытом ([good-joint-states.txt](good-joint-states.txt)).
