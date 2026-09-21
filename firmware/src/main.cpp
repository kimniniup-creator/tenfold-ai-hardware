#include <Arduino.h>
#include <Preferences.h>
#include <M5Unified.h>

// P0 newline JSON transport: acknowledge only after Preferences has committed it.
// This firmware accepts offer/event/query; it deliberately never stores inbox text or cloud credentials.
Preferences journal; String line; uint32_t seq=0; String phase="READY";
void reply(const String& s){ Serial.println(s); }
void setup(){ auto cfg=M5.config(); M5.begin(cfg); Serial.begin(115200); journal.begin("tenfold",false); seq=journal.getUInt("seq",0); phase=journal.getString("phase","READY"); M5.Display.setTextSize(2); M5.Display.println("TENFOLD"); reply("{\"type\":\"hello\",\"protocol\":1,\"device_id\":\"m5sticks3-p0\",\"last_seq\":"+String(seq)+"}"); }
void persist(const String& offer){ journal.putString("offer",offer); journal.putString("phase",phase); journal.putUInt("seq",seq); }
void handle(String s){ if(s.length()>4096){reply("{\"type\":\"error\",\"code\":\"too_large\"}");return;} if(s.indexOf("\"type\":\"offer\"")>=0){ phase="READY";persist(s); reply("{\"type\":\"ack\",\"persisted\":true,\"state\":\"READY\",\"last_seq\":"+String(seq)+"}");M5.Display.println("READY 1/10");return;} if(s.indexOf("\"type\":\"event\"")>=0){seq++; if(s.indexOf("complete")>=0)phase="DONE";if(s.indexOf("seal")>=0)phase="SEALED";persist(journal.getString("offer","{}"));reply("{\"type\":\"event\",\"persisted\":true,\"seq\":"+String(seq)+",\"state\":\""+phase+"\",\"pending_sync\":false}");M5.Display.println(phase);return;} if(s.indexOf("\"type\":\"query\"")>=0)reply("{\"type\":\"status\",\"persisted\":true,\"state\":\""+phase+"\",\"last_seq\":"+String(seq)+"}");else reply("{\"type\":\"error\",\"code\":\"unknown_type\"}"); }
void loop(){M5.update();while(Serial.available()){char c=(char)Serial.read();if(c=='\n'){handle(line);line="";}else line+=c;}}
