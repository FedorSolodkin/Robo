# ПР04. Параметры ноды patrol

Все выводы ниже — реальный stdout и коды завершения из контейнера
`osrf/ros:lyrical-desktop-full@sha256:e6b1cb53…` (`ROS_DOMAIN_ID=16`); полные
файлы лежат рядом, имена указаны в скобках. Реализация — коммит
`160d91a71ff9c9bf465a68439cd45cc54642d08c`.

## Стадия 1. Собрать

Нода `patrol` из ПР03 получила три параметра. Допустимы только конечные числа
из диапазона; проверка выполняется **до** изменения таймера и состояния.

| Параметр | По умолчанию | Допустимо |
|---|---|---|
| `linear_speed` | 0.5 м/с | 0 … 1 |
| `turn_rate` | 0.3 рад/с | −1 … 1 |
| `publish_hz` | 10.0 Гц | 1 … 30 |

Как это устроено в `src/patrol/patrol/patrol.py`:

- `validate_param(name, value)` — чистая функция: отвергает нечисла, `NaN`,
  `±inf` и значения вне диапазона, возвращает `(ok, reason)`.
- `_on_set_parameters` работает в два прохода: сначала проверяет **все**
  параметры пакета, и только если всё допустимо, применяет побочные эффекты.
  Недопустимое значение возвращает `successful=False`, и ни таймер, ни
  сохранённые значения не меняются.
- При допустимой смене `publish_hz` создаётся новый таймер с периодом
  `1/publish_hz`, затем прежний таймер уничтожается через `destroy_timer`;
  одновременно живёт ровно один таймер (проверяет тест).
- `choose_cmd(last_pose, linear_speed, turn_rate)` — чистая функция выбора
  команды: до первой позы нулевая, дальше — текущие параметры.

Значения по умолчанию на запущенной ноде ([good-02-defaults.txt](good-02-defaults.txt)):

```
$ ros2 param get /patrol linear_speed   -> Double value is: 0.5
$ ros2 param get /patrol turn_rate      -> Double value is: 0.3
$ ros2 param get /patrol publish_hz     -> Double value is: 10.0
```

### Допустимое изменение 10 → 5 Гц меняет поток

Нода запущена как `ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel`.
Частота измерялась `timeout --signal=INT 20s ros2 topic hz /turtle1/cmd_vel`
(окно 20 с, потому что CLI под эмуляцией стартует несколько секунд):

| Шаг | Команда | Результат | Файл |
|---|---|---|---|
| до | — | `average rate: 10.002` (окно 150 сообщений) | [good-03](good-03-hz-default.txt) |
| смена | `ros2 param set /patrol publish_hz 5.0` | `Set parameter successful` | [good-04](good-04-set-hz-5.txt) |
| после | — | `average rate: 4.999` (окно 75) | [good-05](good-05-hz-after-5.txt) |

### Недопустимые значения отклоняются, значение и поток прежние

| Команда | Результат | Файл |
|---|---|---|
| `ros2 param set /patrol publish_hz 0.0` | `Setting parameter failed: publish_hz must be within [1.0, 30.0]` | [good-06](good-06-set-hz-0.txt) |
| затем `ros2 param get /patrol publish_hz` | `Double value is: 5.0` (старое значение) | [good-07](good-07-get-hz-after-0.txt) |
| поток после отклонения | `average rate: 5.002` — таймер не тронут | [good-08](good-08-hz-after-0.txt) |
| `ros2 param set /patrol publish_hz -5.0` | `Setting parameter failed: publish_hz must be within [1.0, 30.0]` | [good-09](good-09-set-hz-negative.txt) |
| `ros2 param set /patrol publish_hz .nan` | `Setting parameter failed: publish_hz must be finite` | [good-10](good-10-set-hz-nan.txt) |
| `ros2 param set /patrol linear_speed 5.0` | `Setting parameter failed: linear_speed must be within [0.0, 1.0]` | [good-11](good-11-set-speed-out-of-range.txt) |
| `ros2 param set /patrol turn_rate -0.5` | `Set parameter successful` | [good-12](good-12-set-turn-ok.txt) |

(`.nan` — запись YAML для числа NaN; обычное слово `nan` CLI разбирает как
строку и отклонил бы по типу ещё до проверки диапазона.) Итоговые значения
после всех попыток — `0.5`, `-0.5`, `5.0` ([good-13](good-13-get-final.txt)),
нода жива ([good-14](good-14-node-alive.txt)).

### Тесты

`python3 -m pytest src/patrol/test -v` → **44 passed, 1 skipped**
([tests.txt](tests.txt); пропущен только сгенерированный `test_copyright`).
В тестах чистой функции `validate_param` проверены: изменение 10 → 5 Гц,
ноль, отрицательное значение, `NaN`, `±inf`, значения на границах диапазона и
нечисловые аргументы; тесты живой ноды проверяют пересоздание таймера, один
оставшийся таймер, отказ без изменения состояния, пакет из двух параметров
с одним недопустимым и отказ при недопустимом значении на старте.

## Стадия 2. Сломать

В отдельной ветке `defect/pr04-no-hz-check`, коммит
`b65ac4dd42248bd50d51d44b6d028dc483fb520c`, проверка частоты временно
отключена двумя строками в начале `validate_param`:

```python
if name == 'publish_hz':
    return True, ''
```

Те же тесты ([defect-tests.txt](defect-tests.txt)): **13 failed, 24 passed**.
Падают случаи `publish_hz` = 0.0, −5.0, 0.9, 30.1, `NaN`, `inf`, `−inf` в тестах
чистой функции и `0.0`, −5.0, `NaN`, `inf`, 31.0 плюс недопустимый старт в
тестах живой ноды. Конкретный отказ для нуля:

```
_restart_timer
    new_timer = self.create_timer(1.0 / hz, self._on_timer)
ZeroDivisionError: division by zero
```

На работающей ноде ([defect-live-*.txt](defect-live-02-set-hz-0.txt)):

- `ros2 param set /patrol publish_hz 0.0` **не получает ответа** и убивается
  `timeout` (`!rclpy.ok()`, `exit=124`) — узел упал, не отправив результат;
- в stderr ноды — тот же `ZeroDivisionError`, процесс завершился с кодом 1
  ([defect-live-06](defect-live-06-patrol-stderr.txt));
- `ros2 node list` показывает только `/turtlesim`, `/patrol` исчез
  ([defect-live-03](defect-live-03-node-list.txt));
- `ros2 param get /patrol publish_hz` → `Node not found`, `exit=1`
  ([defect-live-04](defect-live-04-get-hz.txt));
- поток команд остановился: `ros2 topic hz` за 20 с не получил ни одного
  сообщения ([defect-live-05](defect-live-05-hz-after.txt)); до сбоя было
  `average rate: 10.001` ([defect-live-01](defect-live-01-hz-before.txt)).

Один пропущенный `0` разрушил не только параметр, но и всё активное состояние
ноды: она перестала публиковать команды.

## Стадия 3. Доказать

Проверка возвращена (ветка `main`, код без двух строк дефекта). Тот же набор
тестов ([fixed-tests.txt](fixed-tests.txt)): **37 passed** вместо 13 упавших.
Тот же живой сценарий на исправленной ноде:

| Шаг | Результат | Файл |
|---|---|---|
| поток до | `average rate: 9.999` | [fixed-live-01](fixed-live-01-hz-before.txt) |
| `ros2 param set /patrol publish_hz 0.0` | `Setting parameter failed: publish_hz must be within [1.0, 30.0]`, `exit=0` | [fixed-live-02](fixed-live-02-set-hz-0.txt) |
| `ros2 node list` | `/patrol` и `/turtlesim` на месте | [fixed-live-03](fixed-live-03-node-list.txt) |
| `ros2 param get /patrol publish_hz` | `Double value is: 10.0` — значение прежнее | [fixed-live-04](fixed-live-04-get-hz.txt) |
| поток после | `average rate: 10.005` — поток прежний | [fixed-live-05](fixed-live-05-hz-after.txt) |

Отклонение нуля сохраняет значение и поток, а допустимая смена 10 → 5 Гц
меняет поток (см. стадию 1).

## Сервис `/clear` и действие `/turtle1/rotate_absolute`

Готовый сервис turtlesim вызван ([good-15](good-15-service-clear.txt)):

```
$ ros2 service call /clear std_srvs/srv/Empty
requester: making request: std_srvs.srv.Empty_Request()
response:
std_srvs.srv.Empty_Response()
```

Действие найдено через `ros2 action list -t` ([good-17](good-17-action-list.txt)):

```
/turtle1/rotate_absolute [turtlesim_msgs/action/RotateAbsolute]
```

`ros2 action info /turtle1/rotate_absolute -t` показывает один сервер
`/turtlesim` и ноль клиентов ([good-18](good-18-action-info.txt)); `/clear`
в `ros2 service list -t` числится сервисом ([good-16](good-16-service-list.txt)).

**Отличие запроса и цели.** Запрос сервиса (`/clear`) — разовое обращение:
клиент отправляет один запрос и ждёт один ответ, не получая ни промежуточного
состояния, ни возможности остановить обработку. Цель действия
(`/turtle1/rotate_absolute`) — долгая задача: сервер принимает цель, пока она
выполняется, присылает feedback, в конце возвращает результат, а клиент может
отменить цель до завершения.
