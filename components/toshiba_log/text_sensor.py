import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import CONF_TYPE

from . import CONF_TOSHIBA_LOG_ID, ToshibaLog

# StatusData enum-like fields (status-frames.hpp) -- see ToshibaLog::set_status_text_sensor()
STATUS_TEXT_SENSOR_TYPES = {
    "operation_mode": text_sensor.text_sensor_schema(),
}

CONFIG_SCHEMA = cv.typed_schema(
    {
        key: schema.extend(
            {cv.GenerateID(CONF_TOSHIBA_LOG_ID): cv.use_id(ToshibaLog)}
        )
        for key, schema in STATUS_TEXT_SENSOR_TYPES.items()
    },
    key=CONF_TYPE,
    lower=True,
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_TOSHIBA_LOG_ID])
    sens = await text_sensor.new_text_sensor(config)
    cg.add(hub.set_status_text_sensor(config[CONF_TYPE], sens))
