# ПР01. Окружение и граф ROS 2

Результат работы с `turtlesim` в ROS 2 Lyrical: запуск готовых нод, наблюдение
графа, измерение частоты позы и опыт с `ROS_DOMAIN_ID`.

- [Граф, измерения и объяснение сбоя](evidence/pr01/graph.md)
- [Окружение](evidence/pr01/environment.json)
- [Отчёт ROS Doctor](evidence/pr01/doctor.txt)
- [Сводный отчёт для проверки](evidence/pr01/report.json)
- [Использование ИИ](AI_USAGE.md)

## Среда

Ubuntu 26.04, ROS 2 Lyrical, Gazebo Jetty 10.4.0. Обе ноды запущены в одном
Docker-контейнере на Windows 10 + WSL2, графическое окно turtlesim выведено на
хост через WSLg. Образ зафиксирован по digest:

```text
osrf/ros:lyrical-desktop-full@sha256:e6b1cb530b65588279681db53784e264ce5cf83f2cc33e689d27d6024d7f3ebe
```

Команды ниже выполняются из корня репозитория, внутри контейнера на WSL2 с
рабочими `DISPLAY` и проброшенным сокетом WSLg:

```bash
docker run -d --name pr01-submission --hostname pr01-submission \
  -e DISPLAY=:0 -e ROS_DOMAIN_ID=16 \
  -v /mnt/wslg/.X11-unix:/tmp/.X11-unix \
  -v /mnt/wslg:/mnt/wslg \
  -v "$PWD:/work" -w /work \
  osrf/ros:lyrical-desktop-full@sha256:e6b1cb530b65588279681db53784e264ce5cf83f2cc33e689d27d6024d7f3ebe \
  sleep infinity
```

В каждом из терминалов A/B/C подключаюсь к **этому же** контейнеру:

```bash
docker exec -it pr01-submission bash
source /opt/ros/lyrical/setup.bash
export ROS_DOMAIN_ID=16
cd /work
```

## Исправный граф

В A запускаю симулятор:

```bash
ros2 run turtlesim turtlesim_node
```

В B запускаю управление и нажимаю стрелку ↑, оставляя фокус в терминале B:

```bash
ros2 run turtlesim turtle_teleop_key
```

В C сохраняю сведения:

```bash
mkdir -p evidence/pr01
ros2 doctor --report > evidence/pr01/doctor.txt 2>&1
ros2 node list --no-daemon --spin-time 2 > evidence/pr01/nodes-before.txt
ros2 topic list -t > evidence/pr01/topics.txt
ros2 node info /turtlesim > evidence/pr01/turtlesim-info.txt
ros2 node info /teleop_turtle > evidence/pr01/teleop-info.txt
ros2 topic type /turtle1/pose > evidence/pr01/pose-type.txt
ros2 topic echo /turtle1/pose --once > evidence/pr01/pose-before.txt
```

Измерение частоты неподвижной черепахи, 15 секунд, завершение по SIGINT
(аналогично `Ctrl+C`; ненулевой код `timeout` означает истечение интервала, а не
отсутствие сообщений):

```bash
TIMEFORMAT='elapsed_seconds=%R'
{ time timeout --signal=INT 15s ros2 topic hz /turtle1/pose \
  > evidence/pr01/pose-hz.txt 2>&1; } 2> evidence/pr01/pose-hz-duration.txt
printf 'exit=%s\n' "$?" > evidence/pr01/pose-hz-exit.txt
```

После одного нажатия ↑ в B сохраняю новую позу в C:

```bash
ros2 topic echo /turtle1/pose --once > evidence/pr01/pose-after-key-working.txt
```

## Разрыв связи

A продолжает работать в домене 16. В B останавливаю teleop через `Ctrl+C` и
запускаю заново в другом домене:

```bash
export ROS_DOMAIN_ID=17
ros2 run turtlesim turtle_teleop_key
```

В C выполняю проверку в домене 17 (`POSE_TYPE` сохранён после исправного
запуска):

```bash
export ROS_DOMAIN_ID=17
POSE_TYPE=$(cat evidence/pr01/pose-type.txt)
ros2 node list --no-daemon --spin-time 2 > evidence/pr01/nodes-broken.txt
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once \
  > evidence/pr01/pose-broken.txt 2>&1
printf 'exit=%s\n' "$?" > evidence/pr01/pose-broken-exit.txt
```

Нажимаю ↑ в B ещё раз. Независимая проверка неподвижности — одно чтение позы
из домена симулятора (16), текущий домен C остаётся 17:

```bash
ROS_DOMAIN_ID=16 ros2 topic echo /turtle1/pose --once \
  > evidence/pr01/pose-after-key-broken-control.txt
```

## Восстановление

В B останавливаю teleop через `Ctrl+C` и возвращаю его в исходный домен:

```bash
export ROS_DOMAIN_ID=16
ros2 run turtlesim turtle_teleop_key
```

В C повторяю тот же тест доставки:

```bash
export ROS_DOMAIN_ID=16
ros2 node list --no-daemon --spin-time 2 > evidence/pr01/nodes-fixed.txt
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once \
  > evidence/pr01/pose-fixed.txt 2>&1
printf 'exit=%s\n' "$?" > evidence/pr01/pose-fixed-exit.txt
```

Снова нажимаю ↑ в B, сохраняю результат в C:

```bash
ros2 topic echo /turtle1/pose --once > evidence/pr01/pose-after-key-fixed.txt
```

Значения, сравнение состояний и причина сбоя разобраны в
[graph.md](evidence/pr01/graph.md).

## Как составлен environment.json

В том же контейнере получены `/etc/os-release`, `uname -m`, `ROS_DISTRO`,
`ROS_DOMAIN_ID`, `gz sim --versions` и фактический RMW:

```bash
python3 -c 'from rclpy.utilities import get_rmw_implementation_identifier; print(get_rmw_implementation_identifier())'
```

Сырые значения сохранены в [environment-sources.txt](evidence/pr01/environment-sources.txt)
и перенесены в [environment.json](evidence/pr01/environment.json). Digest
совпадает с образом в команде `docker run`.

## Проверка отчёта

```bash
python3 -m json.tool evidence/pr01/environment.json > /dev/null
python3 .course-kit/v1/tools/check_practice.py PR01 --submission .
```

В истории два коммита: первый содержит README и CI-workflow, второй —
`evidence/pr01/` и `AI_USAGE.md`. Поле `report.commit` указывает на первый.
После push проверяется вкладка **Actions**: там должен завершиться зелёным
run второго коммита.
