# ПР02 — всё по этой задаче в одном месте

- **Код:** [../../src/turtle_bringup/](../../src/turtle_bringup/) — пакет с launch-файлом `turtlesim`
- **Отчёт для проверки:** [report.json](report.json)
- **Разбор команд (3 Linux-команды, `>` vs `|`, `source`):** [commands.md](commands.md)
- **Типы сообщений:** [types.md](types.md)
- **Декларация ИИ:** [../../AI_USAGE.md](../../AI_USAGE.md) (раздел "ПР02")
- **Evidence-коммит (сдаётся на проверку):** `69eb574b578a5fa25f23faa8882620ca76ed0a89`
  — [diff](https://github.com/FedorSolodkin/Robo/commit/69eb574b578a5fa25f23faa8882620ca76ed0a89)
  · [репозиторий на этот момент](https://github.com/FedorSolodkin/Robo/tree/69eb574b578a5fa25f23faa8882620ca76ed0a89)
- **Коммит реализации** (пакет + CI): `81aa9a96020144acbd445d183a757299fd21c38c`
- **CI run:** https://github.com/FedorSolodkin/Robo/actions/runs/36956101645 ✅

## Как запустить локально
```bash
docker exec -it pr01-submission bash
source /opt/ros/lyrical/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=16
ros2 launch turtle_bringup sim.launch.py
```

## Файлы показаний
| Файл | Что в нём |
|---|---|
| [build-empty.txt](build-empty.txt) | сборка пустого пакета (до launch-файла) |
| [build.txt](build.txt) | сборка после добавления `launch/sim.launch.py` |
| [launch-run.txt](launch-run.txt) / [launch-nodes.txt](launch-nodes.txt) | запуск и чистая остановка `ros2 launch` |
| [movement-commands.txt](movement-commands.txt) | `ros2 topic pub` двигает черепаху |
| [break-fix.txt](break-fix.txt) | разрыв по неправильному имени топика (`/cmd_vel` vs `/turtle1/cmd_vel`) и исправление |

Полный разбор команд и выводов — [commands.md](commands.md).
