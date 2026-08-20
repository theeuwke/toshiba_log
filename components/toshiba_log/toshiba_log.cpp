#include "estia-serial.h"
#include "toshiba_log.h"
#include "esphome/core/log.h"
#include <cmath>
#include <utility>

namespace toshiba_log {

static const char *TAG = "toshiba_log";

void ToshibaLog::setup() {
  ESP_LOGI(TAG, "UART logger started");
  estiaSerial.reset(new EstiaSerial(*this));
}

void ToshibaLog::loop() {
  /* 
  while (available()) {
    uint8_t b;
    read_byte(&b);
    ESP_LOGD(TAG, "RX: %02X", b);
  }
  */

  switch (estiaSerial->sniffer()) {
    case EstiaSerial::sniff_frame_pending:
      Serial.println(EstiaFrame::stringify(estiaSerial->getSniffedFrame()));
      if (estiaSerial->frameAck != 0) {
        ESP_LOGD(TAG, "frame 0x%04X acked\n", estiaSerial->getAck());
      } else if (estiaSerial->newStatusData) {
        StatusData data = estiaSerial->getStatusData();
        printStatusData(data);
        publish_status_entities_(data);
        // request sensors data after extended status data received (every 30s)
        if (active_requests_enabled_ && data.extendedData) {
          if (data.pump1 ||                                                      // when pump1 is on every 30s
              millis() - requestDataTimer >= requestDataOffInterval - 1000) {    // when pump1 is off every 5min
            requestDataTimer = millis();
            // request exactly the data points that have a configured sensor: entry
            // (see set_data_sensor()) -- no separate list to keep in sync, and if
            // none are configured we deliberately don't fall back to a default list
            DataToRequest wanted;
            for (auto& kv : data_sensors_) { wanted.push_back(kv.first); }
            if (!wanted.empty()) {
              estiaSerial->requestSensorsData(std::move(wanted));
            }
          }
        }
      }
      break;
    case EstiaSerial::sniff_idle:
      // to avoid data collisions write and request data here
      if (estiaSerial->newSensorsData) {
        publish_data_sensors_();
      }
      break;
    }
}

void ToshibaLog::publish_data_sensors_() {
  for (auto& sensor : estiaSerial->getSensorsData()) {
    auto it = data_sensors_.find(sensor.first);
    if (it == data_sensors_.end()) { continue; }
    // data is error code, skip multiplier
    if (sensor.second.value <= EstiaSerial::err_not_exist) {
      it->second->publish_state(NAN);
    } else {
      it->second->publish_state(sensor.second.value * sensor.second.multiplier);
    }
  }
}

void ToshibaLog::publish_status_entities_(StatusData& data) {
  if (data.error != StatusFrame::err_ok) { return; }

  auto publish_sensor = [&](const char* key, uint8_t value) {
    auto it = status_sensors_.find(key);
    if (it != status_sensors_.end()) { it->second->publish_state(value); }
  };
  publish_sensor("hot_water_target", data.hotWaterTarget);
  publish_sensor("zone1_target", data.zone1Target);
  publish_sensor("zone2_target", data.zone2Target);
  if (data.extendedData) {
    publish_sensor("hot_water_target2", data.hotWaterTarget2);
    publish_sensor("zone1_target2", data.zone1Target2);
    publish_sensor("zone2_target2", data.zone2Target2);
  }

  auto publish_binary = [&](const char* key, bool value) {
    auto it = status_binary_sensors_.find(key);
    if (it != status_binary_sensors_.end()) { it->second->publish_state(value); }
  };
  publish_binary("cooling", data.cooling);
  publish_binary("heating", data.heating);
  publish_binary("hot_water", data.hotWater);
  publish_binary("auto_mode", data.autoMode);
  publish_binary("quiet_mode", data.quietMode);
  publish_binary("night_mode", data.nightMode);
  publish_binary("backup_heater", data.backupHeater);
  publish_binary("cooling_cmp", data.coolingCMP);
  publish_binary("heating_cmp", data.heatingCMP);
  publish_binary("hot_water_heater", data.hotWaterHeater);
  publish_binary("hot_water_cmp", data.hotWaterCMP);
  publish_binary("pump1", data.pump1);
  publish_binary("defrost_in_progress", data.defrostInProgress);
  publish_binary("night_mode_active", data.nightModeActive);

  auto ts_it = status_text_sensors_.find("operation_mode");
  if (ts_it != status_text_sensors_.end()) {
    ts_it->second->publish_state(data.operationMode == 0x06 ? "heating" : "cooling");
  }
}

void ToshibaLog::printStatusData(StatusData& data) {
	if (data.error == StatusFrame::err_ok) {
		ESP_LOGD(TAG, "operationMode:     %s\n", data.operationMode == 0x06 ? "heating" : "cooling");
		ESP_LOGD(TAG, "cooling:           %s\n", data.cooling ? "on" : "off");
		ESP_LOGD(TAG, "heating:           %s\n", data.heating ? "on" : "off");
		ESP_LOGD(TAG, "hotWater:          %s\n", data.hotWater ? "on" : "off");
		ESP_LOGD(TAG, "autoMode:          %s\n", data.autoMode ? "on" : "off");
		ESP_LOGD(TAG, "quietMode:         %s\n", data.quietMode ? "on" : "off");
		ESP_LOGD(TAG, "nightMode:         %s\n", data.nightMode ? "on" : "off");
		ESP_LOGD(TAG, "backupHeater:      %s\n", data.backupHeater ? "on" : "off");
		ESP_LOGD(TAG, "coolingCMP:        %s\n", data.coolingCMP ? "on" : "off");
		ESP_LOGD(TAG, "heatingCMP:        %s\n", data.heatingCMP ? "on" : "off");
		ESP_LOGD(TAG, "hotWaterHeater:    %s\n", data.hotWaterHeater ? "on" : "off");
		ESP_LOGD(TAG, "hotWaterCMP:       %s\n", data.hotWaterCMP ? "on" : "off");
		ESP_LOGD(TAG, "pump1:             %s\n", data.pump1 ? "on" : "off");
		ESP_LOGD(TAG, "hotWaterTarget:    %u\n", data.hotWaterTarget);
		ESP_LOGD(TAG, "zone1Target:       %u\n", data.zone1Target);
		ESP_LOGD(TAG, "zone2Target:       %u\n", data.zone2Target);
		if (data.extendedData) {
			ESP_LOGD(TAG, "hotWaterTarget2:   %u\n", data.hotWaterTarget2);
			ESP_LOGD(TAG, "zone1Target2:      %u\n", data.zone1Target2);
			ESP_LOGD(TAG, "zone2Target2:      %u\n", data.zone2Target2);
		}
		ESP_LOGD(TAG, "defrostInProgress: %s\n", data.defrostInProgress ? "true" : "false");
		ESP_LOGD(TAG, "nightModeActive:   %s\n", data.nightModeActive ? "true" : "false");
		ESP_LOGD(TAG, "extendedData:      %s\n", data.extendedData ? "true" : "false");
	}
	ESP_LOGD(TAG, "error:             %u\n", data.error);
}

}  // to namespace toshiba_log