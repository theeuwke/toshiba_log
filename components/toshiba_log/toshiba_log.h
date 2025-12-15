#pragma once
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "estia-serial.h"

namespace toshiba_log {

class ToshibaLog : public esphome::Component,
                     public esphome::uart::UARTDevice {

  public:
    ~ToshibaLog() = default;
    void setup() override;
    void loop() override;
  private:
    void printStatusData(StatusData& data);
    u_long requestDataOffInterval = 300000;    // data update interval when heat pump is doing nothing
    u_long requestDataTimer = requestDataOffInterval;
    bool requestData = false;
    std::unique_ptr<EstiaSerial> estiaSerial;
};

}  // namespace toshiba_log