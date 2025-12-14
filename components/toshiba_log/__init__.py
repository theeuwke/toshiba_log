import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID

toshiba_log_ns = cg.esphome_ns.namespace("toshiba_log")
ToshibaLog = toshiba_log_ns.class_("ToshibaLog", cg.Component)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(ToshibaLog),
}).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)