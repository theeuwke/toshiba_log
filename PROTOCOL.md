# Tu2C bus protocol notes

> **Compatibility scope:** this document describes the Tu2C bus variant used by
> **R32-generation Toshiba Estia heat pumps**, where every frame begins with
> the sync bytes `0xA0 0x00` (`FRAME_BEGIN`, `frame.hpp:45`). **Older
> R410-generation Estia units use a different Tu2C/TCC-Link variant whose
> frames begin with `0xF0 0xF0`** and are structured differently. This
> component's frame-sync detection, CRC, and decoders only understand the
> `0xA0 0x00` variant -- it does not detect, decode, or otherwise support
> R410-generation units. Nothing here should be read as a general TCC-Link/Tu2C
> reference.

This is a consolidation of what has been reverse-engineered so far, gathered
from inline comments across `frame.hpp`, `data-frames.hpp`,
`commands-frames.hpp`, and `status-frames.hpp`. It documents existing
knowledge only -- no new reverse engineering was done to produce it.

## Physical bus

- 2400 baud, 8 data bits, **even** parity, 1 stop bit (8E1).
- Appears to be a shared, half-duplex line: a device's own transmitted bytes
  loop back on its own RX (see `estia-serial.cpp`'s `write()`/`read()`, which
  suppress self-echo in software since ESPHome's UART API has no hardware
  half-duplex switch).
- No documented bus arbitration/collision-avoidance beyond "only transmit
  while nothing else is being received" (see `toshiba_log.cpp`'s
  `sniff_idle` state).

## Frame layout

```
offset  0    1    2     3        4-10 (7 bytes)              11+           last 2
        AA   00   TYPE  DATALEN  SRC(2) DST(2) DATATYPE(2)   PAYLOAD...    CRC16
```

- `FRAME_BEGIN = 0xA000` -- the 2-byte sync marker (`frame.hpp:45`).
- Byte 2: frame **type** (see table below).
- Byte 3: declared length of everything from byte 4 onward, up to but
  excluding the CRC (`FRAME_DATA_LEN_OFFSET`).
- Bytes 4-10: a 7-byte data header: 2-byte `src`, 2-byte `dst`, 2-byte
  `dataType` (`FRAME_SRC_OFFSET=5`, `FRAME_DST_OFFSET=7`,
  `FRAME_DATA_TYPE_OFFSET=9`).
- Bytes 11+: payload, length varies per frame kind.
- Last 2 bytes: CRC-16/MCRF4XX (`EstiaFrame::crc16()`, `frame.cpp`), computed
  over every preceding byte.
- Overall frame length ranges from 13 (`FRAME_MIN_LEN`) to 45
  (`FRAME_MAX_LEN`) bytes.

### Addressing (`src`/`dst` values)

| Constant | Value | Meaning |
|---|---|---|
| `FRAME_SRC_DST_MASTER` | `0x0800` | the hydro/indoor unit ("master") |
| `FRAME_SRC_DST_REMOTE` | `0x0040` | the wired remote controller |
| `FRAME_SRC_DST_BROADCAST` | `0x00FE` | broadcast (e.g. periodic status frames) |

### Frame types (byte offset 2)

| Constant | Value | Meaning |
|---|---|---|
| `FRAME_TYPE_CTRL_FRAME` | `0x10` | heartbeat |
| `FRAME_TYPE_CMD` | `0x11` | a command (mode/operation/switch/temperature change) |
| `FRAME_TYPE_REQ_DATA` | `0x17` | a data-point request |
| `FRAME_TYPE_ACK` | `0x18` | acknowledgement of a command |
| `FRAME_TYPE_RES_DATA` | `0x1A` | a data-point response |
| `FRAME_TYPE_UPDATE` | `0x1C` | short (17-byte) periodic status broadcast |
| `FRAME_TYPE_STATUS2` | `0x55` | (decoded structurally, not currently used for status decode) |
| `FRAME_TYPE_STATUS` | `0x58` | long/extended (31-byte) periodic status broadcast, every ~30s |

### Data types (2-byte field at offset 9)

| Constant | Value | Meaning |
|---|---|---|
| `FRAME_DATA_TYPE_HEARTBEAT` | `0x008A` | heartbeat |
| `FRAME_DATA_TYPE_STATUS` | `0x03C6` | status broadcast |
| `FRAME_DATA_TYPE_MODE_CHANGE` | `0x03C4` | auto/quiet/night mode set |
| `FRAME_DATA_TYPE_OPERATION_MODE` | `0x03C0` | cooling/heating mode set |
| `FRAME_DATA_TYPE_OPERATION_SWITCH` | `0x0041` | cooling/heating/hot-water on/off |
| `FRAME_DATA_TYPE_TEMPERATURE_CHANGE` | `0x03C1` | setpoint change |
| `FRAME_DATA_TYPE_SPECIAL_CMD` | `0x0015` | special command (e.g. forced defrost) |
| `FRAME_DATA_TYPE_DATA_REQUEST` | `0x0080` | request a data point |
| `FRAME_DATA_TYPE_DATA_RESPONSE` | `0x00EF` | response to a data-point request |
| `FRAME_DATA_TYPE_ACK` | `0x00A1` | command acknowledgement |
| `FRAME_DATA_TYPE_SHORT_STATUS` | `0x002B` | short status variant |

## CRC

CRC-16/MCRF4XX, computed over every byte except the trailing 2 CRC bytes
(`EstiaFrame::crc16()`, `frame.cpp`).

## Status broadcasts

The master periodically (every ~30s) broadcasts a status frame -- short
(17-byte payload, `FRAME_TYPE_UPDATE`) or long/extended (31-byte payload,
`FRAME_TYPE_STATUS`). The long variant carries a second set of setpoints and
is what triggers this component's optional active-request cycle (see
`toshiba_log.cpp`). Decoded fields (`status-frames.cpp`), all offsets
relative to the payload:

| Field | Offset | Decode |
|---|---|---|
| `operationMode` | 11 | `(byte & 0xE0) >> 5` -- `0x05`=cooling, `0x06`=heating |
| `cooling` | 11 | `(byte & 0xA1) == 0xA1` |
| `heating` | 11 | `(byte & 0xC1) == 0xC1` |
| `hotWater` | 11 | bit 1 |
| `autoMode` | 12 | bit 2 |
| `quietMode` | 12 | bit 4 |
| `nightMode` | 12 | bit 5 |
| `backupHeater` | 13 | bit 0 |
| `coolingCMP` | 13 | bit 1, when `operationMode == 0x05` |
| `heatingCMP` | 13 | bit 1, when `operationMode == 0x06` |
| `hotWaterHeater` | 13 | bit 2 |
| `hotWaterCMP` | 13 | bit 3 |
| `pump1` | 13 | bit 4 |
| `hotWaterTarget` / `zone1Target` / `zone2Target` | 14 / 15 / 16 | `byte / 2 - 16` (°C) |
| `hotWaterTarget2` / `zone1Target2` / `zone2Target2` | 17 / 18 / 19 | same formula, long frame only |
| `defrostInProgress` | 17 (short) / 21 (long) | bit 1 |
| `nightModeActive` | 17 (short) / 21 (long) | bit 4 |

## Actively-requestable data points (`data-frames.hpp`)

A remote requests a single data point by code (`DataReqFrame`); the master
responds with its value (`DataResFrame`). Known codes and their scaling:

| Name | Code | Scale | Meaning |
|---|---|---|---|
| `tc` | `0x04` | x1 °C | condensed temperature |
| `twi` | `0x06` | x1 °C | water inlet temperature |
| `two` | `0x07` | x1 °C | water outlet temperature |
| `tho` | `0x08` | x1 °C | water heater outlet temperature |
| `tfi` | `0x09` | x1 °C | floor inlet temperature |
| `ttw` | `0x0A` | x1 °C | hot water temperature |
| `mix` | `0x0B` | x1 step | mixing valve position |
| `lps` | `0x0E` | x1/10 kPa | low pressure |
| `sw_ver` | `0x0F` | -- | software version |
| `ctrl_hw_temp` | `0x10` | x1 °C | hot water control temperature |
| `ctrl_zone1_temp` | `0x11` | x1 °C | zone 1 control temperature |
| `ctrl_zone2_temp` | `0x12` | x1 °C | zone 2 control temperature |
| `wf` | `0xC0` | x10 L/min | water flow |
| `te` | `0x60` | x1 °C | heat exchange temperature |
| `to` | `0x61` | x1 °C | outside temperature |
| `td` | `0x62` | x1 °C | discharge temperature |
| `ts` | `0x63` | x1 °C | suction temperature |
| `ths` | `0x65` | x1 °C | heat sink temperature |
| `ct` | `0x6A` | x1/10 A | current |
| `tl` | `0x6D` | x1 °C | heat exchanger coil temperature |
| `cmp` | `0x70` | x1 Hz | compressor speed |
| `fan1` / `fan2` | `0x72` / `0x73` | x1 RPM | outdoor fan speed |
| `pmv` | `0x74` | x1/10 pulse | outdoor PMV position |
| `hps` | `0x7A` | x1/10 kPa | high pressure |
| `hp_on_time` | `0xF0` | x1/100 h | microcomputer energized accumulation |
| `hw_cmp_on_time` | `0xF1` | x1/100 h | hot water compressor ON accumulation |
| `cool_cmp_on_time` | `0xF2` | x1/100 h | cooling compressor ON accumulation |
| `heat_cmp_on_time` | `0xF3` | x1/100 h | heating compressor ON accumulation |
| `pump1_on_time` | `0xF4` | x1/100 h | pump 1 ON accumulation |
| `hw_e_heater_on_time` | `0xF5` | x1/100 h | hot water E-heater accumulation |
| `backup_heater_on_time` | `0xF6` | x1/100 h | backup E-heater accumulation |
| `boost_heater_on_time` | `0xF7` | x1/100 h | booster E-heater accumulation |

> Note: a few of the "x1/10" scaled codes above (`lps`, `ct`, `pmv`, `hps`)
> and `wf`'s "x10" comment don't cleanly match the `multiplier` values
> actually stored in `requestsMap` (e.g. `wf` is commented "x10" but stores a
> `0.1` multiplier). This is pre-existing and unconfirmed against real bus
> captures -- double-check these specific values against your own hardware.

## Commands (`commands-frames.hpp`) -- not exposed to Home Assistant by this component

For reference, the following outgoing commands are implemented in the C++
layer but not currently wired to any ESPHome entity (out of scope for the
sensor-reporting/request-toggle feature):

- **Mode set** (`SetModeFrame`, data type `0x03C4`): `auto` (`0x01`), `quiet`
  (`0x04`), `night` (`0x88`) -- value at payload offset 12, `1<<bit` when on,
  `0x00` when off.
- **Operation mode** (`OperationMode`, data type `0x03C0`): `cooling`
  (`0x05`) / `heating` (`0x06`) at payload offset 11.
- **On/off switch** (`SwitchFrame`, data type `0x0041`): cooling/heating
  (`0x23` on / `0x22` off) or hot water (`0x2C` on / `0x28` off) at payload
  offset 11.
- **Temperature set** (`TemperatureFrame`, data type `0x03C1`): encoded as
  `(temp + 16) * 2` at payload offsets 12/13/15 (zone1/zone2) or 14 (hot
  water).
- **Forced defrost** (`ForcedDefrostFrame`, data type `0x0015`, command code
  `0x46`): `0x01` on / `0x00` off at payload offset 13.
