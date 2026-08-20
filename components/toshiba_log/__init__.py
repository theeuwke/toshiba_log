import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID
from esphome.components import uart as uart

CODEOWNERS = ["@bart-theeuwes-ampel"]
DEPENDENCIES = ["uart"]
AUTO_LOAD = ["sensor", "text_sensor", "binary_sensor", "switch"]
MULTI_CONF = True

CONF_TOSHIBA_LOG_ID = "toshiba_log_id"

toshiba_log_ns = cg.esphome_ns.namespace("toshiba_log")
ToshibaLog = toshiba_log_ns.class_("ToshibaLog", cg.Component, uart.UARTDevice)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(ToshibaLog),
}).extend(cv.COMPONENT_SCHEMA).extend(uart.UART_DEVICE_SCHEMA)

# this component's frame sync detection (0xA0 0x00) only matches the
# R32-generation Estia Tu2C bus; enforce the bus settings that variant uses.
FINAL_VALIDATE_SCHEMA = uart.final_validate_device_schema(
    "toshiba_log",
    baud_rate=2400,
    require_rx=True,
    require_tx=False,
    data_bits=8,
    parity="EVEN",
    stop_bits=1,
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)