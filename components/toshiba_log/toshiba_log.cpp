#include "estia-serial.h"
#include "toshiba_log.h"
#include "esphome/core/log.h"

namespace toshiba_log {

static const char *TAG = "toshiba_log";

void ToshibaLog::setup() {
  ESP_LOGI(TAG, "UART logger started");
  estiaSerial = std::make_unique<EstiaSerial>(*this);
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
        // request sensors data after extended status data received (every 30s)
        if (data.extendedData) {
          if (data.pump1 ||                                                      // when pump1 is on every 30s
              millis() - requestDataTimer >= requestDataOffInterval - 1000) {    // when pump1 is off every 5min
            requestDataTimer = millis();
            // request update for default data points (config.h -> SENSORS_DATA_TO_REQUEST)
            estiaSerial->requestSensorsData();
            // or request update for chosen data points
            // estiaSerial->requestSensorsData({"twi", "two", "wf"}, true)
          }
        }
      }
      break;
    case EstiaSerial::sniff_idle:
      // to avoid data collisions write and request data here
      if (estiaSerial->newSensorsData) {
        for (auto& sensor : estiaSerial->getSensorsData()) {
          ESP_LOGD(TAG,"%s :", sensor.first.c_str());
          // data is error code skip multiplier
          if (sensor.second.value <= EstiaSerial::err_not_exist) {
            ESP_LOGD(TAG, "%d", sensor.second.value);
          } else {
            ESP_LOGD(TAG, "%f", sensor.second.value * sensor.second.multiplier);
          }
          ESP_LOGD(TAG, "\n");
        }
      }
      break;
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