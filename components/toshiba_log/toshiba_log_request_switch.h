#pragma once
#include "esphome/components/switch/switch.h"
#include "toshiba_log.h"

namespace toshiba_log {

class ToshibaLogRequestSwitch : public esphome::switch_::Switch {
  public:
    void set_parent(ToshibaLog* parent) { parent_ = parent; }

  protected:
    void write_state(bool state) override {
      parent_->set_active_requests_enabled(state);
      publish_state(state);
    }
    ToshibaLog* parent_;
};

}  // namespace toshiba_log
