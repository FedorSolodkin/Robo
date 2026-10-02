# ПР01 — всё по этой задаче в одном месте

- **Код:** нет (ПР01 — только README + CI, кода не требует)
- **Отчёт для проверки:** [report.json](report.json)
- **Полный разбор опыта:** [graph.md](graph.md)
- **Декларация ИИ:** [../../AI_USAGE.md](../../AI_USAGE.md) (раздел "ПР01" вверху файла)
- **Evidence-коммит (сдаётся на проверку):** `a5aa53866a2347c93514d21f3dce056fe7950bd8`
  — [diff](https://github.com/FedorSolodkin/Robo/commit/a5aa53866a2347c93514d21f3dce056fe7950bd8)
  · [репозиторий на этот момент](https://github.com/FedorSolodkin/Robo/tree/a5aa53866a2347c93514d21f3dce056fe7950bd8)
- **Коммит реализации** (README + workflow): `4af5ccafe792f4eeffd4d06ead718a7b9cca6d06`
- **CI run:** https://github.com/FedorSolodkin/Robo/actions/runs/36956265280 ✅

## Файлы показаний
| Файл | Что в нём |
|---|---|
| [doctor.txt](doctor.txt) | `ros2 doctor --report` |
| [environment.json](environment.json) / [environment-sources.txt](environment-sources.txt) | ОС, ROS_DISTRO, RMW, версия Gazebo |
| [nodes-before.txt](nodes-before.txt) / [nodes-broken.txt](nodes-broken.txt) / [nodes-fixed.txt](nodes-fixed.txt) | `ros2 node list` в рабочем / разорванном / восстановленном состоянии |
| [topics.txt](topics.txt), [pose-type.txt](pose-type.txt) | список топиков, тип позы |
| [turtlesim-info.txt](turtlesim-info.txt) / [teleop-info.txt](teleop-info.txt) | `ros2 node info` по каждой ноде |
| [pose-hz.txt](pose-hz.txt) + duration/exit | частота `/turtle1/pose` (~125 Гц за 15 с) |
| [pose-before.txt](pose-before.txt) → [pose-after-key-working.txt](pose-after-key-working.txt) | поза до/после реального нажатия ↑ |
| [pose-broken.txt](pose-broken.txt) + exit, [pose-after-key-broken-control.txt](pose-after-key-broken-control.txt) | разрыв связи при другом `ROS_DOMAIN_ID` |
| [pose-fixed.txt](pose-fixed.txt) + exit, [pose-after-key-fixed.txt](pose-after-key-fixed.txt) | восстановление связи |

Суть опыта и объяснение причины сбоя — целиком в [graph.md](graph.md).
