import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from esphome.const import (
    CONF_TYPE,
    DEVICE_CLASS_COLD,
    DEVICE_CLASS_HEAT,
    DEVICE_CLASS_RUNNING,
)

from . import CONF_TOSHIBA_LOG_ID, ToshibaLog

# StatusData boolean flags (status-frames.hpp) -- see ToshibaLog::set_status_binary_sensor()
STATUS_BINARY_SENSOR_TYPES = {
    "cooling": binary_sensor.binary_sensor_schema(device_class=DEVICE_CLASS_COLD),
    "heating": binary_sensor.binary_sensor_schema(device_class=DEVICE_CLASS_HEAT),
    "hot_water": binary_sensor.binary_sensor_schema(device_class=DEVICE_CLASS_RUNNING),
    "auto_mode": binary_sensor.binary_sensor_schema(),
    "quiet_mode": binary_sensor.binary_sensor_schema(),
    "night_mode": binary_sensor.binary_sensor_schema(),
    "backup_heater": binary_sensor.binary_sensor_schema(device_class=DEVICE_CLASS_HEAT),
    "cooling_cmp": binary_sensor.binary_sensor_schema(device_class=DEVICE_CLASS_RUNNING),
    "heating_cmp": binary_sensor.binary_sensor_schema(device_class=DEVICE_CLASS_RUNNING),
    "hot_water_heater": binary_sensor.binary_sensor_schema(device_class=DEVICE_CLASS_HEAT),
    "hot_water_cmp": binary_sensor.binary_sensor_schema(device_class=DEVICE_CLASS_RUNNING),
    "pump1": binary_sensor.binary_sensor_schema(device_class=DEVICE_CLASS_RUNNING),
    "defrost_in_progress": binary_sensor.binary_sensor_schema(device_class=DEVICE_CLASS_COLD),
    "night_mode_active": binary_sensor.binary_sensor_schema(),
}

CONFIG_SCHEMA = cv.typed_schema(
    {
        key: schema.extend(
            {cv.GenerateID(CONF_TOSHIBA_LOG_ID): cv.use_id(ToshibaLog)}
        )
        for key, schema in STATUS_BINARY_SENSOR_TYPES.items()
    },
    key=CONF_TYPE,
    lower=True,
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_TOSHIBA_LOG_ID])
    sens = await binary_sensor.new_binary_sensor(config)
    cg.add(hub.set_status_binary_sensor(config[CONF_TYPE], sens))
