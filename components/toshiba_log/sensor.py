import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    CONF_TYPE,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_DURATION,
    DEVICE_CLASS_FREQUENCY,
    DEVICE_CLASS_PRESSURE,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLUME_FLOW_RATE,
    ENTITY_CATEGORY_DIAGNOSTIC,
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    UNIT_AMPERE,
    UNIT_CELSIUS,
    UNIT_HERTZ,
    UNIT_HOUR,
    UNIT_REVOLUTIONS_PER_MINUTE,
)

from . import CONF_TOSHIBA_LOG_ID, ToshibaLog

# requestsMap-backed data points (data-frames.hpp): configuring one of these
# is what tells ToshibaLog to actively request it when active requests are
# enabled -- see ToshibaLog::set_data_sensor()
DATA_SENSOR_TYPES = {
    "tc": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "twi": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "two": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "tho": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "tfi": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "ttw": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "mix": sensor.sensor_schema(unit_of_measurement="step", accuracy_decimals=0, state_class=STATE_CLASS_MEASUREMENT),
    "lps": sensor.sensor_schema(unit_of_measurement="kPa", accuracy_decimals=1, device_class=DEVICE_CLASS_PRESSURE, state_class=STATE_CLASS_MEASUREMENT),
    "sw_ver": sensor.sensor_schema(accuracy_decimals=0, entity_category=ENTITY_CATEGORY_DIAGNOSTIC),
    "ctrl_hw_temp": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "ctrl_zone1_temp": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "ctrl_zone2_temp": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "wf": sensor.sensor_schema(unit_of_measurement="L/min", accuracy_decimals=1, device_class=DEVICE_CLASS_VOLUME_FLOW_RATE, state_class=STATE_CLASS_MEASUREMENT),
    "te": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "to": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "td": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "ts": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "ths": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "ct": sensor.sensor_schema(unit_of_measurement=UNIT_AMPERE, accuracy_decimals=1, device_class=DEVICE_CLASS_CURRENT, state_class=STATE_CLASS_MEASUREMENT),
    "tl": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "cmp": sensor.sensor_schema(unit_of_measurement=UNIT_HERTZ, accuracy_decimals=0, device_class=DEVICE_CLASS_FREQUENCY, state_class=STATE_CLASS_MEASUREMENT),
    "fan1": sensor.sensor_schema(unit_of_measurement=UNIT_REVOLUTIONS_PER_MINUTE, accuracy_decimals=0, state_class=STATE_CLASS_MEASUREMENT),
    "fan2": sensor.sensor_schema(unit_of_measurement=UNIT_REVOLUTIONS_PER_MINUTE, accuracy_decimals=0, state_class=STATE_CLASS_MEASUREMENT),
    "pmv": sensor.sensor_schema(unit_of_measurement="step", accuracy_decimals=1, state_class=STATE_CLASS_MEASUREMENT),
    "hps": sensor.sensor_schema(unit_of_measurement="kPa", accuracy_decimals=1, device_class=DEVICE_CLASS_PRESSURE, state_class=STATE_CLASS_MEASUREMENT),
    "hp_on_time": sensor.sensor_schema(unit_of_measurement=UNIT_HOUR, accuracy_decimals=2, device_class=DEVICE_CLASS_DURATION, state_class=STATE_CLASS_TOTAL_INCREASING, entity_category=ENTITY_CATEGORY_DIAGNOSTIC),
    "hw_cmp_on_time": sensor.sensor_schema(unit_of_measurement=UNIT_HOUR, accuracy_decimals=2, device_class=DEVICE_CLASS_DURATION, state_class=STATE_CLASS_TOTAL_INCREASING, entity_category=ENTITY_CATEGORY_DIAGNOSTIC),
    "cool_cmp_on_time": sensor.sensor_schema(unit_of_measurement=UNIT_HOUR, accuracy_decimals=2, device_class=DEVICE_CLASS_DURATION, state_class=STATE_CLASS_TOTAL_INCREASING, entity_category=ENTITY_CATEGORY_DIAGNOSTIC),
    "heat_cmp_on_time": sensor.sensor_schema(unit_of_measurement=UNIT_HOUR, accuracy_decimals=2, device_class=DEVICE_CLASS_DURATION, state_class=STATE_CLASS_TOTAL_INCREASING, entity_category=ENTITY_CATEGORY_DIAGNOSTIC),
    "pump1_on_time": sensor.sensor_schema(unit_of_measurement=UNIT_HOUR, accuracy_decimals=2, device_class=DEVICE_CLASS_DURATION, state_class=STATE_CLASS_TOTAL_INCREASING, entity_category=ENTITY_CATEGORY_DIAGNOSTIC),
    "hw_e_heater_on_time": sensor.sensor_schema(unit_of_measurement=UNIT_HOUR, accuracy_decimals=2, device_class=DEVICE_CLASS_DURATION, state_class=STATE_CLASS_TOTAL_INCREASING, entity_category=ENTITY_CATEGORY_DIAGNOSTIC),
    "backup_heater_on_time": sensor.sensor_schema(unit_of_measurement=UNIT_HOUR, accuracy_decimals=2, device_class=DEVICE_CLASS_DURATION, state_class=STATE_CLASS_TOTAL_INCREASING, entity_category=ENTITY_CATEGORY_DIAGNOSTIC),
    "boost_heater_on_time": sensor.sensor_schema(unit_of_measurement=UNIT_HOUR, accuracy_decimals=2, device_class=DEVICE_CLASS_DURATION, state_class=STATE_CLASS_TOTAL_INCREASING, entity_category=ENTITY_CATEGORY_DIAGNOSTIC),
}

# StatusData numeric targets (status-frames.hpp) -- passively decoded only,
# never actively requested -- see ToshibaLog::set_status_sensor()
STATUS_SENSOR_TYPES = {
    "hot_water_target": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "zone1_target": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "zone2_target": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "hot_water_target2": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "zone1_target2": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
    "zone2_target2": sensor.sensor_schema(unit_of_measurement=UNIT_CELSIUS, accuracy_decimals=0, device_class=DEVICE_CLASS_TEMPERATURE, state_class=STATE_CLASS_MEASUREMENT),
}

ALL_SENSOR_TYPES = {**DATA_SENSOR_TYPES, **STATUS_SENSOR_TYPES}

CONFIG_SCHEMA = cv.typed_schema(
    {
        key: schema.extend(
            {cv.GenerateID(CONF_TOSHIBA_LOG_ID): cv.use_id(ToshibaLog)}
        )
        for key, schema in ALL_SENSOR_TYPES.items()
    },
    key=CONF_TYPE,
    lower=True,
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_TOSHIBA_LOG_ID])
    sens = await sensor.new_sensor(config)
    type_key = config[CONF_TYPE]
    if type_key in DATA_SENSOR_TYPES:
        cg.add(hub.set_data_sensor(type_key, sens))
    else:
        cg.add(hub.set_status_sensor(type_key, sens))
