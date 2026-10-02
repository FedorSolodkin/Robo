# Граф, измерения и объяснение сбоя

## Граф в исправном состоянии

Две ноды в домене 16:

```
[teleop_turtle] --publish--> /turtle1/cmd_vel --subscribe--> [turtlesim]
[turtlesim] --publish--> /turtle1/pose
```

- `/turtle1/cmd_vel` — тип `geometry_msgs/msg/Twist`.
- `/turtle1/pose` — тип `turtlesim_msgs/msg/Pose` (см. [pose-type.txt](pose-type.txt)).

Список нод и топиков в рабочем состоянии: [nodes-before.txt](nodes-before.txt), [topics.txt](topics.txt),
подробности по каждой ноде — [turtlesim-info.txt](turtlesim-info.txt), [teleop-info.txt](teleop-info.txt).

## Частота публикации позы

Измерение `ros2 topic hz /turtle1/pose` за 15 секунд на неподвижной черепахе показывает
среднюю частоту около **125 Гц** (см. [pose-hz.txt](pose-hz.txt)); фактическая
длительность замера — 15.976 c ([pose-hz-duration.txt](pose-hz-duration.txt)), команда
завершилась по таймеру ([pose-hz-exit.txt](pose-hz-exit.txt): `exit=124`, это ожидаемое
завершение по сигналу таймаута, а не отсутствие сообщений).

## Три состояния позиции черепахи

| Состояние | x | y | theta | Файл |
|---|---|---|---|---|
| Спавн (до движения) | 5.5444 | 5.5444 | 0.0 | [pose-before.txt](pose-before.txt) |
| После одного ↑ (домен 16, рабочий) | 8.9364 | 5.5444 | 0.0 | [pose-after-key-working.txt](pose-after-key-working.txt) |
| После ↑ в чужом домене 17 (контроль из домена 16) | 8.9364 | 5.5444 | 0.0 | [pose-after-key-broken-control.txt](pose-after-key-broken-control.txt) |
| После ↑ уже в восстановленном домене 16 | 11.0889 | 5.5444 | 0.0 | [pose-after-key-fixed.txt](pose-after-key-fixed.txt) |

Координата `x` растёт ровно на одну и ту же величину (~3.39) при каждом реальном
нажатии ↑ в правильном домене, и **не меняется вовсе**, пока пульт находится в
чужом домене — несмотря на то, что клавиша физически была нажата.

## Разрыв связи (смена ROS_DOMAIN_ID)

Пока симулятор (`turtlesim`) работал в домене 16, пульт (`teleop_turtle`) был
перезапущен с `ROS_DOMAIN_ID=17`. Проверка из домена 17:

- `ros2 node list` видит только `/teleop_turtle` — [nodes-broken.txt](nodes-broken.txt).
  Ноды `/turtlesim` в списке нет: она физически не транслирует discovery-пакеты
  в домен 17.
- `ros2 topic echo /turtle1/pose --once` с таймаутом 5 c завершается по таймеру
  без единого сообщения — [pose-broken.txt](pose-broken.txt), код завершения
  `exit=124` ([pose-broken-exit.txt](pose-broken-exit.txt)).

## Причина сбоя

`ROS_DOMAIN_ID` — это не настройка конкретного топика, а параметр DDS-транспорта:
он определяет диапазон UDP-портов, на которых нода объявляет о себе и ищет соседей
(SPDP discovery). Ноды с разным `ROS_DOMAIN_ID` физически не получают друг от
друга ни discovery-пакетов, ни пользовательских сообщений — с точки зрения каждой
из них, соседей просто не существует. Правильный тип сообщения и совпадающее имя
топика (`/turtle1/cmd_vel`) в этой ситуации не помогают: без совпадения домена
подписка никогда не установится.

## Восстановление

Пульт перезапущен обратно с `ROS_DOMAIN_ID=16`. Проверка из домена 16:

- `ros2 node list` снова видит обе ноды — [nodes-fixed.txt](nodes-fixed.txt).
- `ros2 topic echo /turtle1/pose --once` возвращает актуальную позу без таймаута,
  `exit=0` — [pose-fixed.txt](pose-fixed.txt), [pose-fixed-exit.txt](pose-fixed-exit.txt).
- Повторное нажатие ↑ снова двигает черепаху (x: 8.9364 → 11.0889) —
  [pose-after-key-fixed.txt](pose-after-key-fixed.txt).

Это подтверждает: единственная причина сбоя — несовпадение `ROS_DOMAIN_ID`, а не
что-либо иное (тип сообщения, имя топика, состояние симулятора не менялись на
протяжении всего опыта).

## Диагностика окружения

Полный отчёт `ros2 doctor --report` сохранён в [doctor.txt](doctor.txt); версии
и параметры окружения (ОС, `ROS_DISTRO`, `ROS_DOMAIN_ID`, версия Gazebo,
реализация RMW) — в [environment-sources.txt](environment-sources.txt) и
структурированно в [environment.json](environment.json).
