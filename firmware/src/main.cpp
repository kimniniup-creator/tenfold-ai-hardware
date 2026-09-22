#include <Arduino.h>
#include <ArduinoJson.h>
#include <M5Unified.h>
#include <Preferences.h>
#include "pet_assets.h"
#include "reading_state.h"
#include "sticks3_boot.h"
#if __has_include("pet_portrait_assets.h")
#include "pet_portrait_assets.h"
#define PORTRAIT_ASSET 1
#endif

namespace {
constexpr uint32_t WINDOW=10000, COOLDOWN=60000, REPLY_TTL=15000;
Preferences prefs;
ReadingState reading;
ReadingInput input;
const char* modeNames[]={"阅读","工作","运动","学习"};
uint32_t sessionMarks=0;
uint32_t sessionStarted=0,lastSaved=0,readingChanged=0,markFeedback=0;
bool readingDirty=false,storageOk=true,displayReady=false;
void saveReading(){storageOk=prefs.putBytes("reading",&reading,sizeof(reading))==sizeof(reading);readingDirty=!storageOk;lastSaved=millis();}
M5Canvas canvas(&M5.Display);
String session, rx, pending;
bool quiet=false, discard=false, dirty=false, waiting=false, hasPrompt=false;
uint32_t epoch=0, windowId=0, count=0, total=0, held=0, interval=0;
uint32_t windowStart=0, lastPress=0, pressStart=0, lastPrompt=0, requested=0;
uint32_t animStart=0, lastFrame=0, changed=0, messageAt=0;
String message="我在这里。", source="LOCAL";
pet_assets::State replyState=pet_assets::State::Happy;
// One bounded outgoing frame; never wait for a disconnected host.
bool send(JsonDocument& doc){if(!pending.isEmpty()||!Serial)return false;if(doc["type"].as<String>()=="hello"){doc["display_ready"]=displayReady;doc["mode"]=reading.mode;doc["asset"]="portrait-mono-24";}serializeJson(doc,pending);pending+='\n';if(pending.length()>768){pending="";return false;}return true;}
void hello(){JsonDocument d;d["type"]="hello";d["protocol"]=2;d["build"]="reading-0.2";d["chip"]=ESP.getChipModel();d["session"]=session;d["epoch"]=epoch;d["quiet"]=quiet;d["presses_total"]=total;d["interactions_lifetime"]=reading.interactions;d["reading_session"]=reading.session;d["marks_total"]=reading.markCount;d["growth_stage"]=reading.interactions>=100?"grown":"young";d["storage_ok"]=storageOk;d["state_selftest"]=readingSelfTest();d["width"]=M5.Display.width();d["height"]=M5.Display.height();d["board"]=(int)M5.getBoard();send(d);}
void flush(){if(!Serial){pending="";return;}int room=Serial.availableForWrite();if(room<=0||pending.isEmpty())return;size_t n=min((size_t)room,pending.length());Serial.write((const uint8_t*)pending.c_str(),n);pending.remove(0,n);}
bool validText(const String& t){return t=="我在。"||t=="我在，陪你待会儿。"||t=="嗯，接住了。"||t=="慢慢来就好。"||t=="安静待着，也很好。";}
void receive(const String& line){JsonDocument d;if(deserializeJson(d,line)||!d.is<JsonObject>())return;
 String type=d["type"]|"";if(type=="hello_request"){hello();return;}
 if(type=="reading_query"){JsonDocument out;out["type"]="reading_status";out["protocol"]=2;out["reading_session"]=reading.session;out["mode"]=reading.mode;out["interactions_lifetime"]=reading.interactions;out["marks_total"]=reading.markCount;out["storage_ok"]=storageOk;auto marks=out["marks"].to<JsonArray>();uint32_t first=reading.markCount>8?reading.markCount-8:0;for(uint32_t n=first;n<reading.markCount;n++){auto& m=reading.marks[n%16];auto row=marks.add<JsonArray>();row.add(m.session);row.add(m.elapsed);row.add(m.mode);row.add(m.ordinal);row.add(m.interaction);}send(out);return;}
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
void render(uint32_t now){if(now-lastFrame<40)return;lastFrame=now;canvas.fillScreen(TFT_BLACK);
 canvas.setFont(&fonts::efontCN_12);canvas.setTextColor(TFT_WHITE);canvas.setCursor(8,10);canvas.print(reading.mode==0?"一起读一会儿":"陪你待会儿");canvas.setCursor(8,29);canvas.print(modeNames[reading.mode]);canvas.print(" · 陪伴");
#ifdef PORTRAIT_ASSET
 auto state=M5.BtnA.isPressed()?pet_portrait::State::Press:(now-animStart<700?pet_portrait::State::Rebound:(markFeedback&&now-markFeedback<1800?pet_portrait::State::Mark:(quiet?pet_portrait::State::Rest:pet_portrait::State::Idle)));
 auto frame=pet_portrait::frameIndex(reading.interactions>=100?pet_portrait::Stage::Grown:pet_portrait::Stage::Young,state,now-animStart);
 for(int y=0;y<32;y++)for(int x=0;x<32;x++)if(pet_portrait::pixel(frame,x,y))canvas.fillRect(35+x*2,74+y*2,2,2,TFT_WHITE);
#else
 auto state=M5.BtnA.isPressed()?pet_assets::State::Press:(now-animStart<700?replyState:(quiet?pet_assets::State::Rest:((now%4800)<180?pet_assets::State::Blink:pet_assets::State::Idle)));
 auto frame=pet_assets::frameIndex(state,now-animStart);
 for(int y=0;y<32;y++)for(int x=0;x<32;x++){auto p=pet_assets::pixel(frame,x,y);if(p)canvas.fillRect(35+x*2,61+y*2,2,2,pet_assets::kPalette[p]);}
#endif
 canvas.setCursor(8,143);canvas.printf("相伴 %lu 次",(unsigned long)reading.interactions);
 canvas.setCursor(8,156);canvas.printf("本次标记 %lu",(unsigned long)sessionMarks);
 String text=!storageOk?"保存失败，请重试":(markFeedback&&now-markFeedback<1800?"记下这一处":(quiet?"安静待着，也很好。":"我在，陪你待会儿。"));String first=fit(text,119);canvas.setCursor(8,176);canvas.print(first);canvas.setCursor(8,190);canvas.print(fit(text.substring(first.length()),119));canvas.setCursor(8,211);canvas.print("A 互动  B 标记");canvas.setCursor(8,225);canvas.print("长按 B 切换模式");canvas.pushSprite(0,0);
}
}
void setup(){displayReady=beginStickS3();M5.Display.setRotation(0);M5.Display.setBrightness(100);canvas.createSprite(135,240);Serial.begin(115200);Serial.setTxTimeoutMs(0);prefs.begin("pixelpet",false);if(prefs.getBytesLength("reading")==sizeof(reading)){ReadingState saved;if(prefs.getBytes("reading",&saved,sizeof(saved))==sizeof(saved)&&saved.version==1&&saved.mode<4)reading=saved;}if(reading.session<UINT32_MAX)reading.session++;quiet=reading.quiet;saveReading();session=String((uint32_t)ESP.getEfuseMac(),HEX)+"-"+String(esp_random(),HEX);windowStart=sessionStarted=millis();hello();}
void loop(){uint32_t now=millis();M5.update();
 bool a=M5.BtnA.isPressed(),b=M5.BtnB.isPressed();bool aEdge=a&&!input.a;auto event=input.update(reading,a,b,now,now-sessionStarted);
 if(aEdge){pressStart=now;animStart=now;replyState=pet_assets::State::Happy;if(count>0)interval+=min(now-lastPress,WINDOW);lastPress=now;if(count<10000)count++;if(total<UINT32_MAX)total++;message="嗯，接住了。";source="LOCAL";readingDirty=true;readingChanged=now;}
 if(M5.BtnA.isPressed()||M5.BtnA.wasReleased()){held+=now-pressStart;pressStart=now;}
 if(event==ReadingState::Mode){quiet=reading.quiet;epoch++;waiting=false;pending="";saveReading();message="我在这里。";source="LOCAL";hello();}
 if(event==ReadingState::Mark){markFeedback=now;sessionMarks++;saveReading();hello();}
 if(readingDirty&&now-lastSaved>=1000&&(now-readingChanged>=2000||now-lastSaved>=30000))saveReading();
 for(int budget=0;budget<128&&Serial.available();budget++){char c=Serial.read();if(c=='\n'){if(!discard&&!rx.isEmpty())receive(rx);rx="";discard=false;}else if(c!='\r'&&!discard){if(rx.length()>=512){rx="";discard=true;}else rx+=c;}}
 summarize(now);flush();render(now);delay(1);
}
