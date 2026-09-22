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
bool resetMenu=false,resetChord=false;
uint32_t resetHeldAt=0;
bool storageOpened=false,storageLoaded=false,storageFault=false;
size_t storageBootLength=0,storageBootRead=0;
uint32_t storageBootVersion=0,storageBootSession=0;
void saveReading(){
 if(storageFault)return; // Do not repeatedly program a partition that failed readback.
 storageOk=storageOpened&&prefs.putBytes("reading",&reading,sizeof(reading))==sizeof(reading);
 ReadingState check;
 storageOk=storageOk&&prefs.getBytes("reading",&check,sizeof(check))==sizeof(check)&&memcmp(&reading,&check,sizeof(reading))==0;
 storageFault=!storageOk;readingDirty=!storageOk;lastSaved=millis();
}
M5Canvas canvas(&M5.Display);
String session, rx, pending, requestId;
uint32_t loopTicks=0,rxBytes=0,txBytes=0,shortWrites=0,maxLoopGap=0,lastLoop=0;
uint32_t pendingAt=0,expiredFrames=0;
bool quiet=false, discard=false, dirty=false, waiting=false, hasPrompt=false;
uint32_t epoch=0, windowId=0, count=0, total=0, held=0, interval=0;
uint32_t windowStart=0, lastPress=0, pressStart=0, lastPrompt=0, requested=0;
uint32_t animStart=0, lastFrame=0, changed=0, messageAt=0;
String message="", source="LOCAL";
bool resetPet(){
 if(!storageOpened||storageFault)return false;
 ReadingState previous=reading;reading=ReadingState{};reading.session=1;saveReading();
 if(!storageOk){reading=previous;return false;}
 sessionMarks=0;total=count=held=interval=0;quiet=false;markFeedback=0;
 sessionStarted=windowStart=millis();waiting=false;message="";epoch++;return true;
}
pet_assets::State replyState=pet_assets::State::Happy;
// One bounded outgoing frame; never wait for a disconnected host.
bool send(JsonDocument& doc){if(!pending.isEmpty())return false;if(!requestId.isEmpty())doc["request_id"]=requestId;if(doc["type"].as<String>()=="hello"){doc["display_ready"]=displayReady;doc["mode"]=reading.mode;doc["asset"]="portrait-mono-24";}pending="\n";serializeJson(doc,pending);pending+='\n';if(pending.length()>768){pending="";return false;}pendingAt=millis();return true;}
void hello(){JsonDocument d;d["type"]="hello";d["protocol"]=2;d["build"]="reading-0.2";d["chip"]=ESP.getChipModel();d["session"]=session;d["epoch"]=epoch;d["quiet"]=quiet;d["presses_total"]=total;d["interactions_lifetime"]=reading.interactions;d["reading_session"]=reading.session;d["marks_total"]=reading.markCount;d["growth_stage"]=reading.interactions>=100?"grown":"young";d["storage_ok"]=storageOk;d["state_selftest"]=readingSelfTest();d["width"]=M5.Display.width();d["height"]=M5.Display.height();d["board"]=(int)M5.getBoard();send(d);}
void flush(){
 if(pending.isEmpty())return;
 if(millis()-pendingAt>=250){
  // HWCDC can retain a full ring after the host cancels a read. A bounded flush
  // kicks its TX interrupt and discards stale queued bytes if the host is gone.
  Serial.flush();pending="";expiredFrames++;return;
 }
 int room=Serial.availableForWrite();if(room<=0)return;
 size_t n=min((size_t)room,pending.length());
 size_t written=Serial.write((const uint8_t*)pending.c_str(),n);
 txBytes+=written;if(written<n)shortWrites++;pending.remove(0,written);
}
bool validText(const String& t){return t=="我在。"||t=="我在，陪你待会儿。"||t=="嗯，接住了。"||t=="慢慢来就好。"||t=="安静待着，也很好。";}
void receive(const String& line){JsonDocument d;if(deserializeJson(d,line)||!d.is<JsonObject>())return;
 requestId=d["request_id"]|"";if(requestId.length()>32)requestId="";
 String type=d["type"]|"";if(type=="hello_request"){hello();return;}
 if(type=="pet_reset"){if(!d["confirm"].is<bool>()||!d["confirm"].as<bool>())return;JsonDocument out;out["type"]="pet_reset_ack";out["ok"]=resetPet();send(out);return;}
 if(type=="transport_query"){JsonDocument out;out["type"]="transport_status";out["uptime_ms"]=millis();out["loops"]=loopTicks;out["max_loop_gap_ms"]=maxLoopGap;out["rx_bytes"]=rxBytes;out["tx_bytes"]=txBytes;out["short_writes"]=shortWrites;out["pending_bytes"]=pending.length();out["expired_frames"]=expiredFrames;send(out);return;}
 if(type=="storage_query"){JsonDocument out;out["type"]="storage_status";out["opened"]=storageOpened;out["loaded"]=storageLoaded;out["boot_length"]=storageBootLength;out["expected_length"]=sizeof(reading);out["boot_read"]=storageBootRead;out["boot_version"]=storageBootVersion;out["boot_session"]=storageBootSession;out["current_session"]=reading.session;out["readback_ok"]=storageOk;out["current_length"]=prefs.getBytesLength("reading");send(out);return;}
 if(type=="reading_query"){JsonDocument out;out["type"]="reading_status";out["protocol"]=2;out["reading_session"]=reading.session;out["mode"]=reading.mode;out["interactions_lifetime"]=reading.interactions;out["marks_total"]=reading.markCount;out["storage_ok"]=storageOk;auto marks=out["marks"].to<JsonArray>();uint32_t first=reading.markCount>8?reading.markCount-8:0;for(uint32_t n=first;n<reading.markCount;n++){auto& m=reading.marks[n%16];auto row=marks.add<JsonArray>();row.add(m.session);row.add(m.elapsed);row.add(m.mode);row.add(m.ordinal);row.add(m.interaction);}send(out);return;}
 if(type!="reply"||quiet||!waiting||millis()-requested>REPLY_TTL)return;
 if(d["session"].as<String>()!=session||!d["epoch"].is<uint32_t>()||d["epoch"].as<uint32_t>()!=epoch||!d["window"].is<uint32_t>()||d["window"].as<uint32_t>()!=windowId)return;
 String action=d["action"]|"",text=d["text"]|"",origin=d["source"]|"";
 if((action!="blink"&&action!="happy"&&action!="rest")||!validText(text)||(origin!="local"&&origin!="agent"))return;
 for(JsonPair p:d.as<JsonObject>()){String k=p.key().c_str();if(k!="type"&&k!="session"&&k!="epoch"&&k!="window"&&k!="action"&&k!="text"&&k!="source")return;}
 waiting=false;message=text;source=origin=="agent"?"AGENT":"LOCAL";messageAt=millis();animStart=millis();replyState=action=="rest"?pet_assets::State::Rest:(action=="blink"?pet_assets::State::Blink:pet_assets::State::Happy);
}
void summarize(uint32_t now){if(now-windowStart<WINDOW)return;if(waiting&&now-requested<=REPLY_TTL)return;waiting=false;
 // Portrait reading has no visible Agent entry yet: telemetry only, no requests.
 ++windowId;constexpr bool candidate=false;
 JsonDocument d;d["type"]="rhythm";d["protocol"]=2;d["session"]=session;d["epoch"]=epoch;d["window"]=windowId;d["duration_ms"]=now-windowStart;d["presses"]=count;d["held_ms"]=held;d["mean_interval_ms"]=count>1?interval/(count-1):0;d["quiet"]=quiet;d["candidate"]=candidate;
 send(d);
 count=held=interval=0;windowStart=now;
}
String fit(const String& t,int width){String s;for(size_t i=0;i<t.length();){uint8_t c=t[i];size_t n=c<128?1:((c&224)==192?2:((c&240)==224?3:4));if(i+n>t.length())break;String v=s+t.substring(i,i+n);if(canvas.textWidth(v)>width)break;s=v;i+=n;}return s;}
void render(uint32_t now){if(now-lastFrame<40)return;lastFrame=now;canvas.fillScreen(TFT_BLACK);
 canvas.setFont(&fonts::efontCN_12);canvas.setTextColor(TFT_WHITE);
 if(resetMenu){canvas.setCursor(8,65);canvas.print("重新养一只？");canvas.setCursor(8,91);canvas.print("清空互动和标记");canvas.setCursor(8,117);canvas.print("不会重置 M5");canvas.setCursor(8,179);canvas.print("A 确认  B 取消");canvas.pushSprite(0,0);return;}
 canvas.setCursor(8,10);canvas.print(modeNames[reading.mode]);
 canvas.setFont(&fonts::Font0);canvas.setTextDatum(top_right);canvas.drawString(String(reading.interactions)+" / "+String(sessionMarks),127,12);canvas.setTextDatum(top_left);canvas.setFont(&fonts::efontCN_12);
#ifdef PORTRAIT_ASSET
 auto state=M5.BtnA.isPressed()?pet_portrait::State::Press:(now-animStart<700?pet_portrait::State::Rebound:(markFeedback&&now-markFeedback<1800?pet_portrait::State::Mark:(quiet?pet_portrait::State::Rest:pet_portrait::State::Idle)));
 auto frame=pet_portrait::frameIndex(reading.interactions>=100?pet_portrait::Stage::Grown:pet_portrait::Stage::Young,state,now-animStart);
 for(int y=0;y<32;y++)for(int x=0;x<32;x++)if(pet_portrait::pixel(frame,x,y))canvas.fillRect(35+x*2,74+y*2,2,2,TFT_WHITE);
#else
 auto state=M5.BtnA.isPressed()?pet_assets::State::Press:(now-animStart<700?replyState:(quiet?pet_assets::State::Rest:((now%4800)<180?pet_assets::State::Blink:pet_assets::State::Idle)));
 auto frame=pet_assets::frameIndex(state,now-animStart);
 for(int y=0;y<32;y++)for(int x=0;x<32;x++){auto p=pet_assets::pixel(frame,x,y);if(p)canvas.fillRect(35+x*2,61+y*2,2,2,pet_assets::kPalette[p]);}
#endif
 String text=!storageOk?"保存失败，请重启":(markFeedback&&now-markFeedback<1800?"记下这一处":"");String first=fit(text,119);canvas.setCursor(8,176);canvas.print(first);canvas.setCursor(8,190);canvas.print(fit(text.substring(first.length()),119));canvas.setCursor(8,211);canvas.print("A 互动  B 标记");canvas.setCursor(8,225);canvas.print("长按 B 切换模式");canvas.pushSprite(0,0);
}
}
void setup(){displayReady=beginStickS3();M5.Display.setRotation(0);M5.Display.setBrightness(100);canvas.createSprite(135,240);Serial.begin(115200);Serial.setTxTimeoutMs(1);
 storageOpened=prefs.begin("pixelpet",false);
 storageBootLength=prefs.getBytesLength("reading");
 if(storageBootLength==sizeof(reading)){
  ReadingState saved;storageBootRead=prefs.getBytes("reading",&saved,sizeof(saved));
  storageBootVersion=saved.version;storageBootSession=saved.session;
  storageLoaded=storageBootRead==sizeof(saved)&&saved.version==1&&saved.mode<4;
  if(storageLoaded)reading=saved;
 }
 if(reading.session<UINT32_MAX)reading.session++;quiet=reading.quiet;saveReading();session=String((uint32_t)ESP.getEfuseMac(),HEX)+"-"+String(esp_random(),HEX);windowStart=sessionStarted=millis();hello();}
void loop(){uint32_t now=millis();if(lastLoop)maxLoopGap=max(maxLoopGap,now-lastLoop);lastLoop=now;loopTicks++;M5.update();
 bool a=M5.BtnA.isPressed(),b=M5.BtnB.isPressed();
 if(resetMenu){if(!resetChord){if(a&&!input.a){resetPet();resetMenu=false;resetChord=true;}else if(b&&!input.b){resetMenu=false;resetChord=true;}}if(!a&&!b)resetChord=false;input.a=a;input.b=b;render(now);flush();delay(1);return;}
 if(a&&b){if(!resetChord){resetHeldAt=now;resetChord=true;}if(now-resetHeldAt>=3000)resetMenu=true;input.a=a;input.b=b;render(now);flush();delay(1);return;}
 if(resetChord){input.a=a;input.b=b;if(!a&&!b)resetChord=false;render(now);flush();delay(1);return;}
 bool aEdge=a&&!input.a;auto event=input.update(reading,a,b,now,now-sessionStarted);
 if(aEdge){pressStart=now;animStart=now;replyState=pet_assets::State::Happy;if(count>0)interval+=min(now-lastPress,WINDOW);lastPress=now;if(count<10000)count++;if(total<UINT32_MAX)total++;message="嗯，接住了。";source="LOCAL";readingDirty=true;readingChanged=now;}
 if(M5.BtnA.isPressed()||M5.BtnA.wasReleased()){held+=now-pressStart;pressStart=now;}
 if(event==ReadingState::Mode){quiet=reading.quiet;epoch++;waiting=false;pending="";saveReading();message="我在这里。";source="LOCAL";hello();}
 if(event==ReadingState::Mark){markFeedback=now;sessionMarks++;saveReading();hello();}
 if(readingDirty&&now-lastSaved>=1000&&(now-readingChanged>=2000||now-lastSaved>=30000))saveReading();
 for(int budget=0;budget<128&&Serial.available();budget++){char c=Serial.read();rxBytes++;if(c=='\n'){if(!discard&&!rx.isEmpty())receive(rx);requestId="";rx="";discard=false;}else if(c!='\r'&&!discard){if(rx.length()>=512){rx="";discard=true;}else rx+=c;}}
 summarize(now);flush();render(now);delay(1);
}
