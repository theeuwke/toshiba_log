#pragma once
#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/binary_sensor/binary_sensor.h"
#include "estia-serial.h"
#include <map>
#include <string>

namespace toshiba_log {

class ToshibaLog : public esphome::Component,
                     public esphome::uart::UARTDevice {

  public:
    ~ToshibaLog() = default;
    void setup() override;
    void loop() override;

    // requestsMap-backed numeric sensors; being registered here is what marks
    // a data point as "actively request this" when active requests are enabled
    void set_data_sensor(const std::string& type, esphome::sensor::Sensor* sens) { data_sensors_[type] = sens; }
    // StatusData numeric target fields (never actively requested, only passively decoded)
    void set_status_sensor(const std::string& type, esphome::sensor::Sensor* sens) { status_sensors_[type] = sens; }
    void set_status_text_sensor(const std::string& type, esphome::text_sensor::TextSensor* sens) { status_text_sensors_[type] = sens; }
    void set_status_binary_sensor(const std::string& type, esphome::binary_sensor::BinarySensor* sens) { status_binary_sensors_[type] = sens; }
    void set_active_requests_enabled(bool enabled) { active_requests_enabled_ = enabled; }

  private:
    void printStatusData(StatusData& data);
    void publish_status_entities_(StatusData& data);
    void publish_data_sensors_();

    u_long requestDataOffInterval = 300000;    // data update interval when heat pump is doing nothing
    u_long requestDataTimer = requestDataOffInterval;
    bool requestData = false;
    std::unique_ptr<EstiaSerial> estiaSerial;

    std::map<std::string, esphome::sensor::Sensor*> data_sensors_;
    std::map<std::string, esphome::sensor::Sensor*> status_sensors_;
    std::map<std::string, esphome::text_sensor::TextSensor*> status_text_sensors_;
    std::map<std::string, esphome::binary_sensor::BinarySensor*> status_binary_sensors_;
    bool active_requests_enabled_ = false;
};

}  // namespace toshiba_log