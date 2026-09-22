#include <Arduino.h>
#include <ArduinoJson.h>
#include <M5Unified.h>
#include <Preferences.h>
#include "pet_assets.h"
#include "sticks3_boot.h"

namespace {
constexpr uint32_t WINDOW=10000, COOLDOWN=60000, REPLY_TTL=15000;
Preferences prefs;
bool displayReady=false;
M5Canvas canvas(&M5.Display);
String session, rx, pending;
bool quiet=false, discard=false, dirty=false, waiting=false, hasPrompt=false;
uint32_t epoch=0, windowId=0, count=0, total=0, held=0, interval=0;
uint32_t windowStart=0, lastPress=0, pressStart=0, lastPrompt=0, requested=0;
uint32_t animStart=0, lastFrame=0, changed=0, messageAt=0;
String message="我在这里。", source="LOCAL";
pet_assets::State replyState=pet_assets::State::Happy;
// One bounded outgoing frame; never wait for a disconnected host.
bool send(JsonDocument& doc){if(!pending.isEmpty()||!Serial)return false;if(doc["type"].as<String>()=="hello"){doc["build"]="pixel-0.1-displayfix";doc["display_ready"]=displayReady;}serializeJson(doc,pending);pending+='\n';if(pending.length()>768){pending="";return false;}return true;}
void hello(){JsonDocument d;d["type"]="hello";d["protocol"]=2;d["build"]="pixel-0.1";d["chip"]=ESP.getChipModel();d["session"]=session;d["epoch"]=epoch;d["quiet"]=quiet;d["presses_total"]=total;d["width"]=M5.Display.width();d["height"]=M5.Display.height();d["board"]=(int)M5.getBoard();send(d);}
void flush(){if(!Serial){pending="";return;}int room=Serial.availableForWrite();if(room<=0||pending.isEmpty())return;size_t n=min((size_t)room,pending.length());Serial.write((const uint8_t*)pending.c_str(),n);pending.remove(0,n);}
bool validText(const String& t){return t=="我在。"||t=="我在，陪你待会儿。"||t=="嗯，接住了。"||t=="慢慢来就好。"||t=="安静待着，也很好。";}
void receive(const String& line){JsonDocument d;if(deserializeJson(d,line)||!d.is<JsonObject>())return;
 String type=d["type"]|"";if(type=="hello_request"){hello();return;}
 if(type!="reply"||quiet||!waiting||millis()-requested>REPLY_TTL)return;
 if(d["session"].as<String>()!=session||!d["epoch"].is<uint32_t>()||d["epoch"].as<uint32_t>()!=epoch||!d["window"].is<uint32_t>()||d["window"].as<uint32_t>()!=windowId)return;
 String action=d["action"]|"",text=d["text"]|"",origin=d["source"]|"";
 if((action!="blink"&&action!="happy"&&action!="rest")||!validText(text)||(origin!="local"&&origin!="agent"))return;
 for(JsonPair p:d.as<JsonObject>()){String k=p.key().c_str();if(k!="type"&&k!="session"&&k!="epoch"&&k!="window"&&k!="action"&&k!="text"&&k!="source")return;}
 waiting=false;message=text;source=origin=="agent"?"AGENT":"LOCAL";messageAt=millis();animStart=millis();replyState=action=="rest"?pet_assets::State::Rest:(action=="blink"?pet_assets::State::Blink:pet_assets::State::Happy);
}
void summarize(uint32_t now){if(now-windowStart<WINDOW)return;if(waiting&&now-requested<=REPLY_TTL)return;waiting=false;
 ++windowId;bool candidate=!quiet&&count>=3&&(!hasPrompt||now-lastPrompt>=COOLDOWN);
 JsonDocument d;d["type"]="rhythm";d["protocol"]=2;d["session"]=session;d["epoch"]=epoch;d["window"]=windowId;d["duration_ms"]=now-windowStart;d["presses"]=count;d["held_ms"]=held;d["mean_interval_ms"]=count>1?interval/(count-1):0;d["quiet"]=quiet;d["candidate"]=candidate;
 bool queued=send(d);if(candidate&&queued){waiting=true;requested=now;lastPrompt=now;hasPrompt=true;}
 count=held=interval=0;windowStart=now;
}
String fit(const String& t,int width){String s;for(size_t i=0;i<t.length();){uint8_t c=t[i];size_t n=c<128?1:((c&224)==192?2:((c&240)==224?3:4));if(i+n>t.length())break;String v=s+t.substring(i,i+n);if(canvas.textWidth(v)>width)break;s=v;i+=n;}return s;}
void render(uint32_t now){if(now-lastFrame<40)return;lastFrame=now;canvas.fillScreen(0x10E3);
 canvas.setFont(&fonts::efontCN_12);canvas.setTextColor(0xCDB3);canvas.setCursor(9,6);canvas.print(quiet?"安静陪伴":"陪你待一会儿");canvas.setCursor(185,6);canvas.print(source=="AGENT"?"Agent":"本地");
 auto state=M5.BtnA.isPressed()?pet_assets::State::Press:(now-animStart<700?replyState:(quiet?pet_assets::State::Rest:((now%4800)<180?pet_assets::State::Blink:pet_assets::State::Idle)));
 auto frame=pet_assets::frameIndex(state,now-animStart);
 for(int y=0;y<32;y++)for(int x=0;x<32;x++){auto p=pet_assets::pixel(frame,x,y);if(p)canvas.fillRect(88+x*2,24+y*2,2,2,pet_assets::kPalette[p]);}
 String text=quiet?"安静待着，也很好。":message;String first=fit(text,224);canvas.setCursor(8,90);canvas.setTextColor(0xFFFF);canvas.print(first);canvas.setCursor(8,104);canvas.print(fit(text.substring(first.length()),224));canvas.setCursor(8,121);canvas.setTextColor(0x8C71);canvas.print(quiet?"A 轻碰  ·  B 回到陪伴":"A 轻碰  ·  B 安静");canvas.pushSprite(0,0);
}
}
void setup(){displayReady=beginStickS3();M5.Display.setRotation(1);M5.Display.setBrightness(100);canvas.createSprite(240,135);Serial.begin(115200);Serial.setTxTimeoutMs(0);prefs.begin("pixelpet",false);quiet=prefs.getBool("quiet",false);session=String((uint32_t)ESP.getEfuseMac(),HEX)+"-"+String(esp_random(),HEX);windowStart=millis();hello();}
void loop(){uint32_t now=millis();M5.update();
 if(M5.BtnA.wasPressed()){pressStart=now;animStart=now;replyState=pet_assets::State::Happy;if(count>0)interval+=min(now-lastPress,WINDOW);lastPress=now;if(count<10000)count++;if(total<UINT32_MAX)total++;message="嗯，接住了。";source="LOCAL";}
 if(M5.BtnA.isPressed()||M5.BtnA.wasReleased()){held+=now-pressStart;pressStart=now;}
 if(M5.BtnB.wasPressed()){quiet=!quiet;epoch++;waiting=false;pending="";dirty=true;changed=now;message="我在这里。";source="LOCAL";hello();}
 if(dirty&&now-changed>=2000){prefs.putBool("quiet",quiet);dirty=false;}
 for(int budget=0;budget<128&&Serial.available();budget++){char c=Serial.read();if(c=='\n'){if(!discard&&!rx.isEmpty())receive(rx);rx="";discard=false;}else if(c!='\r'&&!discard){if(rx.length()>=512){rx="";discard=true;}else rx+=c;}}
 summarize(now);flush();render(now);delay(1);
}
