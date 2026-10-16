# ПР04 — всё по этой задаче в одном месте

- **Код:** [../../src/patrol/](../../src/patrol/) — нода `patrol` с параметрами и проверкой
- **Разбор опыта (три стадии, команды и вывод):** [parameters.md](parameters.md)
- **Отчёт для проверки:** [report.json](report.json)
- **Декларация ИИ:** [../../AI_USAGE.md](../../AI_USAGE.md) (раздел «ПР04»)
- **Коммит реализации** (`report.commit`): `160d91a71ff9c9bf465a68439cd45cc54642d08c`
- **Дефектный коммит** (стадия «Сломать», ветка `defect/pr04-no-hz-check`):
  `b65ac4dd42248bd50d51d44b6d028dc483fb520c` — красный CI:
  [actions/runs/38850996506](https://github.com/FedorSolodkin/Robo/actions/runs/38850996506)

## Как повторить

```bash
docker exec -it pr01-submission bash
source /opt/ros/lyrical/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
python3 -m pytest src/patrol/test

ros2 launch turtle_bringup sim.launch.py                                   # терминал A
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel             # терминал B
ros2 topic hz /turtle1/cmd_vel                                             # терминал C, ≈ 10
ros2 param set /patrol publish_hz 5.0                                      # successful, ≈ 5
ros2 param set /patrol publish_hz 0.0                                      # failed, значение 5.0 сохранено
```

## Файлы показаний

| Файлы | Что в них |
|---|---|
| [build.txt](build.txt), [tests.txt](tests.txt) | сборка и `pytest src/patrol/test -v` (44 passed, 1 skipped) |
| `good-01…14` | исправная нода: параметры, 10 → 5 Гц, отклонение 0 / −5 / `.nan` / скорости вне диапазона |
| `good-15…18` | `/clear`, список сервисов, `ros2 action list -t`, `ros2 action info` |
| [defect-tests.txt](defect-tests.txt) | те же тесты на дефектной ветке: 13 failed |
| `defect-live-01…06` | `publish_hz 0.0` на дефектной ноде: зависание, `ZeroDivisionError`, нода пропала, поток остановился |
| [fixed-tests.txt](fixed-tests.txt) | те же тесты после возврата проверки: 37 passed |
| `fixed-live-01…06` | `publish_hz 0.0` на исправленной ноде: отклонено, значение и поток прежние |
