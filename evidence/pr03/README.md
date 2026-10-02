# ПР03 — всё по этой задаче в одном месте

- **Код:** [../../src/patrol/](../../src/patrol/) — нода `patrol` (подписка + таймер + чистая функция)
- **Отчёт для проверки:** [report.json](report.json)
- **Демонстрация, разрыв и исправление через remap:** [demo.md](demo.md)
- **Декларация ИИ:** [../../AI_USAGE.md](../../AI_USAGE.md) (раздел "ПР03")
- **Evidence-коммит (сдаётся на проверку):** `74ca576c5f9d21e0dab7cb8743ba557bf753b9f7`
  — [diff](https://github.com/FedorSolodkin/Robo/commit/74ca576c5f9d21e0dab7cb8743ba557bf753b9f7)
  · [репозиторий на этот момент](https://github.com/FedorSolodkin/Robo/tree/74ca576c5f9d21e0dab7cb8743ba557bf753b9f7)
- **Коммит реализации** (нода + тест + CI): `6a9847ecc8433d205043f17933742fa7a17379b3`
- **CI run:** https://github.com/FedorSolodkin/Robo/actions/runs/36958193504 ✅

## Как запустить локально
```bash
docker exec -it pr01-submission bash
source /opt/ros/lyrical/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 launch turtle_bringup sim.launch.py &      # терминал A (или свой терминал)
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel   # с remap — рабочий вариант
```
Без `-r cmd_vel:=/turtle1/cmd_vel` — воспроизводится дефект (см. ниже).

## Файлы показаний
| Файл | Что в нём |
|---|---|
| [build.txt](build.txt) | сборка пакета `patrol` |
| [tests.txt](tests.txt) | `pytest` для чистой функции `select_command` (2/2 passed) |
| [demo-run.txt](demo-run.txt) | полный протокол: разрыв по относительному топику, remap-исправление, измерение частоты 10 Гц, поведение после остановки ноды |

Объяснение `init`/`spin`/callback/`Ctrl+C` и наблюдение про "не мгновенное торможение" — в [demo.md](demo.md).
