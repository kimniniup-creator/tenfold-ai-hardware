# Third-party notices

This release was compiled from the exact dependency set below. The corresponding license texts are included in `licenses/` and travel with the binary release ZIP.

| Component | Exact build version | Source | License file |
| --- | --- | --- | --- |
| M5Unified | 0.2.22 | https://github.com/m5stack/M5Unified | `licenses/M5Unified-LICENSE.txt` (MIT) |
| M5GFX | 0.2.29 | https://github.com/m5stack/M5GFX | `licenses/M5GFX-LICENSE.txt` (MIT) |
| ArduinoJson | 7.4.3 | https://github.com/bblanchon/ArduinoJson | `licenses/ArduinoJson-LICENSE.txt` (MIT) |
| Arduino-ESP32 | PlatformIO package `3.20017.241212+sha.dcc1105b` (upstream 2.0.17) | https://github.com/espressif/arduino-esp32/tree/2.0.17 | `licenses/Arduino-ESP32-LICENSE.txt` (LGPL-2.1-or-later) |
| ESP-IDF SDK bundled by Arduino-ESP32 | 4.4.7, verified from bundled `esp_idf_version.h` | https://github.com/espressif/esp-idf/tree/v4.4.7 | `licenses/ESP-IDF-LICENSE.txt` (Apache-2.0) |

Additional license texts copied from the exact installed packages are included for M5GFX's GFX font material and Arduino-ESP32's compiled libb64 component:

- `licenses/M5GFX-GFXFF-font-LICENSE.txt`
- `licenses/Arduino-ESP32-libb64-LICENSE.txt`

Reproducible build inputs are locked in `firmware/platformio.ini`: PlatformIO Espressif32 6.12.0, M5Unified 0.2.22, M5GFX 0.2.29 and ArduinoJson 7.4.3. The successful build reported Arduino-ESP32 `3.20017.241212+sha.dcc1105b`, esptool.py 4.9.0 and both Espressif GCC toolchains `8.4.0+2021r2-patch5`. Build and flashing tools are not redistributed in this ZIP.
