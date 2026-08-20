# toshiba_log

An ESPHome external component that reads sensor and status data from a
**Toshiba R32-generation Estia heat pump** over its "Tu2C" bus, and exposes it
to Home Assistant. See [`PROTOCOL.md`](PROTOCOL.md) for what's known about the
bus itself, including why this does **not** work with older R410-generation
units.

Adapted from [serek4/estia-serial](https://github.com/serek4/estia-serial).

## What it does

- **Passive sniffing (always on):** decodes the periodic status broadcasts
  the heat pump's master controller sends every ~30s, and publishes them as
  `sensor:`/`binary_sensor:`/`text_sensor:` entities. This works regardless
  of whether active requests (below) are enabled.
- **Active requests (opt-in, off by default):** the wired remote controller
  only puts detailed sensor values (temperatures, flow, pressures, etc.) on
  the bus while it's parked on its sensor-overview screen. To get that data
  reliably, this component can instead directly request specific values from
  the heat pump. This is controlled by a `switch:` entity in Home Assistant
  ("Enable Active Requests") and is **off by default, and always boots off**,
  because it means this device transmits on the bus -- see **Safety** below.

The set of `sensor: platform: toshiba_log` entries you configure (that map to
a `requestsMap` data point -- see `PROTOCOL.md`) doubles as the list of
values requested when active requests are enabled. There's no separate list
to maintain: add a sensor, it gets requested; remove it, it stops being
requested.

## Wiring

2400 baud, 8E1 (8 data bits, even parity, 1 stop bit). RX is required; TX is
only needed if you plan to enable the active-request switch.

```yaml
uart:
  id: uart_bus
  baud_rate: 2400
  parity: EVEN
  data_bits: 8
  stop_bits: 1
  rx_pin: GPIOxx
  tx_pin: GPIOxx    # only needed if you use the "Enable Active Requests" switch

toshiba_log:
  id: heat_pump
  uart_id: uart_bus
```

See [`example.yaml`](example.yaml) for a full example including sensors and
the switch.

## Available `type:` values

- `sensor:` -- any `requestsMap` key from `PROTOCOL.md` (e.g. `twi`, `two`,
  `wf`, `te`, ...), plus the passively-decoded status targets:
  `hot_water_target`, `zone1_target`, `zone2_target`, `hot_water_target2`,
  `zone1_target2`, `zone2_target2`.
- `binary_sensor:` -- `cooling`, `heating`, `hot_water`, `auto_mode`,
  `quiet_mode`, `night_mode`, `backup_heater`, `cooling_cmp`, `heating_cmp`,
  `hot_water_heater`, `hot_water_cmp`, `pump1`, `defrost_in_progress`,
  `night_mode_active`.
- `text_sensor:` -- `operation_mode` (`"heating"` / `"cooling"`).

## Safety: the active-request switch is experimental

Enabling active requests makes this device physically transmit on the bus,
which it shares with the heat pump's own wired remote controller. There is
no confirmed bus arbitration scheme here -- transmission is only attempted
while nothing is being received (to avoid the most obvious collisions), and
the component assumes (unverified) that its own transmitted bytes loop back
on its own RX line, which it filters out in software. If your bus doesn't
behave that way, or a genuine collision occurs, there's no hardware-level
protection against it.

If you enable this switch:
- Watch the logs for excessive `err_timeout` errors on requested sensors
  (means nothing is actually getting through).
- Watch your wired remote controller for any sign of misbehavior.
- Be ready to disable the switch (it always reverts to off on reboot) or
  disconnect the device if anything looks wrong.

## Not currently exposed

Heat pump control (mode, on/off, temperature setpoints, forced defrost) is
implemented in the C++ layer (`commands-frames.hpp`) but not wired to any
Home Assistant entity by this component -- it's read-only plus the
active-request toggle, by design.
