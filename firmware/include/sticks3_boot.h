#pragma once
#include <M5Unified.h>
#include <Preferences.h>

// This product targets the physically verified StickS3, not a generic S3 board.
// M5GFX's NVS hint takes precedence over compile-time board hints. Correct only
// that one cache key; do not erase user NVS or other namespaces.
inline bool beginStickS3(){
  Preferences hint;
  bool cacheOk=hint.begin("M5GFX",false);
  if(cacheOk){
    const uint32_t board=static_cast<uint32_t>(m5::board_t::board_M5StickS3);
    if(hint.getUInt("AUTODETECT",0)!=board)cacheOk=hint.putUInt("AUTODETECT",board)==sizeof(board);
    hint.end();
  }
  delay(150); // PMIC/I2C settling after power-key reset.
  auto config=M5.config();
  config.fallback_board=m5::board_t::board_M5StickS3;
  M5.begin(config);
  return cacheOk&&M5.getBoard()==m5::board_t::board_M5StickS3&&M5.Display.width()>0&&M5.Display.height()>0;
}
