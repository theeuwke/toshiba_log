import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import switch

from . import CONF_TOSHIBA_LOG_ID, ToshibaLog, toshiba_log_ns

ToshibaLogRequestSwitch = toshiba_log_ns.class_(
    "ToshibaLogRequestSwitch", switch.Switch
)

# defaults to restore_mode ALWAYS_OFF -- every reboot starts sniff-only,
# regardless of whatever state was last set from Home Assistant. Enabling
# this switch makes the component actually transmit on the bus, which is
# experimental -- see README.md before turning it on.
CONFIG_SCHEMA = switch.switch_schema(ToshibaLogRequestSwitch).extend(
    {
        cv.GenerateID(CONF_TOSHIBA_LOG_ID): cv.use_id(ToshibaLog),
    }
)


async def to_code(config):
    hub = await cg.get_variable(config[CONF_TOSHIBA_LOG_ID])
    var = await switch.new_switch(config)
    cg.add(var.set_parent(hub))
