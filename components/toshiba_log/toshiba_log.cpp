#include "toshiba_log.h"
#include "esphome/core/log.h"

namespace toshiba_log {

static const char *TAG = "toshiba_log";

void ToshibaLog::setup() {
  ESP_LOGI(TAG, "UART logger started");
}

void ToshibaLog::loop() {
  while (available()) {
    uint8_t b;
    read_byte(&b);
    ESP_LOGD(TAG, "RX: %02X", b);
  }
}

}  // to namespace toshiba_log