# ПР05 — всё по этой задаче в одном месте

- **Код:** [../../src/course_bringup/](../../src/course_bringup/) — launch-файл
  `patrol.launch.py`, ноды `pose_relay` и `sensor_listener`, помощники QoS;
  [../../config/qos-overrides.yaml](../../config/qos-overrides.yaml) — QoS для повтора записи
- **Отчёт для проверки:** [report.json](report.json)
- **Декларация ИИ:** [../../AI_USAGE.md](../../AI_USAGE.md) (раздел «ПР05»)
- **Коммит реализации** (`report.commit`): `fd2e3753a46132f0ce4f6047c41f54b9298ee15a`

## Что устроено

Одна команда поднимает всю систему в пространстве имён `/robot_a`:

```bash
ros2 launch course_bringup patrol.launch.py \
  namespace:=robot_a subscriber_reliability:=best_effort record:=false
```

| Аргумент | По умолчанию | Что делает |
|---|---|---|
| `namespace` | `robot_a` | префикс всех нод и относительных топиков робота |
| `record` | `false` | `true` — запускает `ros2 bag record -s mcap` через `IfCondition` |
| `bag_dir` | `bags/robot_a` | каталог записи (не должен существовать) |
| `subscriber_reliability` | `best_effort` | `reliable` или `best_effort` для `sensor_listener` |

- `turtlesim_node` запускается один раз и глобально (`/turtlesim`, `/turtle1/…`).
- `patrol` из ПР04 внутри `/robot_a`; его `cmd_vel` переназначен в `/turtle1/cmd_vel`.
- `pose_relay` читает `/turtle1/pose` и публикует `sensor_pose` (в системе
  `/robot_a/sensor_pose`) с `best_effort`, `keep_last`, глубина 10.
- `sensor_listener` подписывается на `sensor_pose` с профилем из параметра `reliability`.
- Внутри нод топики относительные (`sensor_pose`, `cmd_vel`), полное имя даёт namespace.

## Как повторить стадии

```bash
docker exec -it pr01-submission bash
cd /work && source install/setup.bash

# Сломать: reliable-подписчик против best_effort-сенсора
ros2 launch course_bringup patrol.launch.py namespace:=robot_a subscriber_reliability:=reliable record:=false
timeout 30s ros2 topic echo /robot_a/sensor_pose --qos-reliability reliable --once        # таймаут, код 124

# Доказать: тот же поток при совместимом профиле + запись
ros2 launch course_bringup patrol.launch.py namespace:=robot_a subscriber_reliability:=best_effort record:=true bag_dir:=evidence/pr05/bag
timeout 30s ros2 topic echo /robot_a/sensor_pose --qos-reliability best_effort --once     # приходит Pose

# Повтор той же записи с тем же QoS
ros2 bag play evidence/pr05/bag --qos-profile-overrides-path config/qos-overrides.yaml --loop
```

## Файлы показаний

| Файл | Что в нём |
|---|---|
| [qos-before.txt](qos-before.txt) | «до»: имена в `/robot_a`, топик виден, 1 издатель и 1 подписчик, но 0 сообщений; `echo` reliable — таймаут; то же на повторе записи |
| [qos-after.txt](qos-after.txt) | «после»: `echo` best_effort получает Pose, listener принимает сообщения; повтор записи; `ros2 bag info` (один поток, 2447 сообщений) |
| [bag-metadata.yaml](bag-metadata.yaml) | копия `bag/metadata.yaml` |
| [bag/](bag/) | запись MCAP (один топик `/robot_a/sensor_pose`) |
| [build.txt](build.txt), [tests.txt](tests.txt) | сборка и `pytest` обоих пакетов (44 + 20 passed, по 1 skipped) |
| [launch-args.txt](launch-args.txt) | `--show-args`: четыре аргумента launch-файла |

## Отличия от примера в методичке

- `timeout 3s` для `ros2 topic echo` заменён на `30s`: контейнер идёт под эмуляцией amd64, одна
  команда `ros2` стартует несколько секунд. «После» при том же таймауте успевает получить
  сообщение, то есть таймаут «до» вызван QoS, а не медленным запуском.
- Запись сделана самим launch-файлом (`record:=true bag_dir:=evidence/pr05/bag`), это та же
  команда `ros2 bag record -s mcap -o … --topics /robot_a/sensor_pose`, но проверяет ветку
  `IfCondition`. Для проигрывания добавлен `--loop`, чтобы запись не кончилась до старта `echo`.
