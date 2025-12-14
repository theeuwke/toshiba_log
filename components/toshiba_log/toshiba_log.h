#pragma once
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"

namespace toshiba_log {

class ToshibaLog : public esphome::Component,
                     public esphome::uart::UARTDevice {

  public:
    ~ToshibaLog();
    void setup() override;
    void loop() override;
};

}  // namespace toshiba_log