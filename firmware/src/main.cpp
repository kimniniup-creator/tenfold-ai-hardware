#include <Arduino.h>
#include <ArduinoJson.h>
#include <M5Unified.h>
#include <Preferences.h>

namespace {
constexpr size_t kMaxFrame=4096;
constexpr uint32_t kUnlockMs=1000;
constexpr uint32_t kConfirmMs=1500;
Preferences store;
String serialLine;
constexpr size_t kCapacity=10;
struct Card {
  String goalText;
  String commandId,cycleId,actionText,doneText,nextText,state="UNPAIRED";
  String pendingDeviceEvents="[]";
  uint32_t revision=0,dayIndex=1,deviceSeq=0,lastHostSeq=0,completedDay=0;
  bool timeTrusted=false;
};
Card cards[kCapacity];
size_t cardCount=0,selected=0;
String deviceId;
uint32_t snapshotVersion=0;
#define goalText cards[selected].goalText
#define commandId cards[selected].commandId
#define cycleId cards[selected].cycleId
#define actionText cards[selected].actionText
#define doneText cards[selected].doneText
#define nextText cards[selected].nextText
#define state cards[selected].state
#define pendingDeviceEvents cards[selected].pendingDeviceEvents
#define revision cards[selected].revision
#define dayIndex cards[selected].dayIndex
#define deviceSeq cards[selected].deviceSeq
#define lastHostSeq cards[selected].lastHostSeq
#define completedDay cards[selected].completedDay
#define timeTrusted cards[selected].timeTrusted
bool operationOpen=false,chooseSeal=false,awaitRelease=false;
uint32_t bothSince=0,confirmSince=0,operationOpenedAt=0;

uint32_t checksum(const String& text){uint32_t hash=2166136261u;for(size_t i=0;i<text.length();++i){hash^=(uint8_t)text[i];hash*=16777619u;}return hash;}
void sendJson(JsonDocument& doc){serializeJson(doc,Serial);Serial.write('\n');}
void error(const char* code){JsonDocument doc;doc["type"]="error";doc["code"]=code;sendJson(doc);}

String fitUtf8(const String& source,int width){String result;for(size_t i=0;i<source.length();){uint8_t c=source[i];size_t count=(c<0x80)?1:((c&0xE0)==0xC0?2:((c&0xF0)==0xE0?3:4));if(i+count>source.length())break;String candidate=result+source.substring(i,i+count);if(M5.Display.textWidth(candidate)>width)break;result=candidate;i+=count;}return result;}
void render(){M5.Display.clear(TFT_BLACK);M5.Display.setTextColor(TFT_GREEN,TFT_BLACK);M5.Display.setFont(&fonts::efontCN_12);M5.Display.setCursor(4,4);M5.Display.printf("TENFOLD  %lu/10\n",(unsigned long)dayIndex);M5.Display.printf("承诺 %u / %u  A切换\n",(unsigned)(cardCount?selected+1:0),(unsigned)cardCount);M5.Display.setTextColor(TFT_WHITE,TFT_BLACK);if(!goalText.isEmpty())M5.Display.println(fitUtf8(goalText,M5.Display.width()-8));M5.Display.println(fitUtf8(actionText,M5.Display.width()-8));M5.Display.setTextColor(TFT_LIGHTGREY,TFT_BLACK);M5.Display.println(state);if(!timeTrusted)M5.Display.println("TIME? 仅查看/封存");if(operationOpen)M5.Display.println(chooseSeal?"B长按: 封存":"B长按: 完成");}

void writeCard(JsonObject doc){doc["command_id"]=commandId;doc["cycle_id"]=cycleId;doc["revision"]=revision;doc["day_index"]=dayIndex;doc["device_seq"]=deviceSeq;doc["last_host_seq"]=lastHostSeq;doc["completed_day"]=completedDay;doc["pending_device_events"]=pendingDeviceEvents;doc["goal"]=goalText;doc["action"]=actionText;doc["done"]=doneText;doc["next"]=nextText;doc["state"]=state;}
String snapshot(uint32_t version){JsonDocument doc;doc["v"]=version;doc["schema"]=2;doc["selected"]=selected;JsonArray list=doc["cards"].to<JsonArray>();size_t previous=selected;for(selected=0;selected<cardCount;selected++)writeCard(list.add<JsonObject>());selected=previous;String json;serializeJson(doc,json);return json;}
String storedSnapshot(const char* slot){size_t length=store.getBytesLength(slot);if(!length)return store.getString(slot,"");if(length>120000)return "";char* bytes=new char[length+1];if(store.getBytes(slot,bytes,length)!=length){delete[] bytes;return "";}bytes[length]=0;String result(bytes);delete[] bytes;return result;}
bool persist(){uint32_t nextVersion=snapshotVersion+1;String json=snapshot(nextVersion);uint32_t sum=checksum(json);const char* slot=(snapshotVersion%2==0)?"slot_b":"slot_a";const char* crc=(snapshotVersion%2==0)?"crc_b":"crc_a";size_t written=store.putBytes(slot,json.c_str(),json.length());size_t crcWritten=store.putUInt(crc,sum);if(written!=json.length()||crcWritten!=sizeof(uint32_t)||storedSnapshot(slot)!=json||store.getUInt(crc,0)!=sum)return false;if(store.putUInt("active",nextVersion)!=sizeof(uint32_t)||store.getUInt("active",0)!=nextVersion)return false;snapshotVersion=nextVersion;return true;}
void readCard(JsonObject doc){commandId=doc["command_id"]|"";cycleId=doc["cycle_id"]|"";revision=doc["revision"]|0;dayIndex=doc["day_index"]|1;deviceSeq=doc["device_seq"]|0;lastHostSeq=doc["last_host_seq"]|0;pendingDeviceEvents=doc["pending_device_events"]|"[]";goalText=doc["goal"]|"";actionText=doc["action"]|"";doneText=doc["done"]|"";nextText=doc["next"]|"";state=doc["state"]|"UNPAIRED";completedDay=doc["completed_day"]|(state=="DONE"?dayIndex:0);timeTrusted=false;}
bool restoreSlot(const char* slot,const char* crc){
 String json=storedSnapshot(slot);if(json.isEmpty()||checksum(json)!=store.getUInt(crc,0))return false;
 JsonDocument doc;if(deserializeJson(doc,json))return false;
 if(doc["schema"]==2){JsonArray list=doc["cards"].as<JsonArray>();if(list.isNull()||list.size()>kCapacity)return false;cardCount=list.size();for(selected=0;selected<cardCount;selected++)readCard(list[selected]);selected=doc["selected"]|0;if(selected>=cardCount)selected=0;}
 else{selected=0;readCard(doc.as<JsonObject>());cardCount=cycleId.isEmpty()?0:1;}
 snapshotVersion=doc["v"]|0;return true;
}
int findCard(const String& id){size_t previous=selected;for(selected=0;selected<cardCount;selected++){if(cycleId==id){int found=selected;selected=previous;return found;}}selected=previous;return -1;}
void selectCard(size_t index){selected=index;operationOpen=false;awaitRelease=false;confirmSince=bothSince=0;}

void restore(){uint32_t active=store.getUInt("active",0);bool ok=(active%2==0)?restoreSlot("slot_a","crc_a"):restoreSlot("slot_b","crc_b");if(!ok)ok=(active%2==0)?restoreSlot("slot_b","crc_b"):restoreSlot("slot_a","crc_a");if(!ok)state="UNPAIRED";timeTrusted=false;}

bool onlyKeys(JsonObject object,const char* const* allowed,size_t count){for(JsonPair pair:object){bool found=false;for(size_t i=0;i<count;i++)if(strcmp(pair.key().c_str(),allowed[i])==0){found=true;break;}if(!found)return false;}return true;}
bool requiredString(JsonObject obj,const char* key,size_t max){return obj[key].is<const char*>()&&strlen(obj[key])>0&&strlen(obj[key])<=max;}
void offerAck(){JsonDocument ack;ack["type"]="ack";ack["protocol"]=1;ack["device_id"]=deviceId;ack["command_id"]=commandId;ack["cycle_id"]=cycleId;ack["revision"]=revision;ack["persisted"]=true;ack["state"]=state;ack["last_seq"]=deviceSeq;sendJson(ack);}
void handleOffer(JsonObject obj){static const char* keys[]={"type","protocol","command_id","cycle_id","revision","day_index","cycle_start_date","local_date","tz","action_short","done_when_short","stop_at","next_step_short","goal_short"};if(!onlyKeys(obj,keys,14)||obj["protocol"].as<int>()!=1||!requiredString(obj,"command_id",72)||!requiredString(obj,"cycle_id",72)||!requiredString(obj,"action_short",240)||!requiredString(obj,"done_when_short",240)||(obj["goal_short"].is<const char*>()&&strlen(obj["goal_short"])>240)||(obj["next_step_short"].is<const char*>()&&strlen(obj["next_step_short"])>240)){error("invalid_offer");return;}String incoming=obj["command_id"].as<String>(),incomingCycle=obj["cycle_id"].as<String>();uint32_t incomingRevision=obj["revision"]|0,incomingDay=obj["day_index"]|0;if(incoming==commandId&&incomingRevision==revision&&incomingCycle==cycleId){offerAck();return;}if(incomingRevision==0||incomingDay<1||incomingDay>10){error("invalid_offer");return;}int found=findCard(incomingCycle);bool added=found<0;size_t previous=selected;if(added){if(cardCount>=kCapacity){error("capacity_full");return;}selectCard(cardCount++);cards[selected]=Card();}else selectCard(found);if(incomingRevision<revision||incomingDay<dayIndex){error("stale_revision");return;}if(incoming==commandId&&incomingRevision==revision){offerAck();return;}if(incomingRevision==revision&&!cycleId.isEmpty()){error("revision_conflict");return;}
  String oldGoal=goalText;String oldCommand=commandId,oldCycle=cycleId,oldAction=actionText,oldDone=doneText,oldNext=nextText,oldState=state;uint32_t oldRevision=revision,oldDay=dayIndex;
  goalText=obj["goal_short"]|"";commandId=incoming;cycleId=incomingCycle;revision=incomingRevision;dayIndex=constrain(incomingDay,1u,10u);actionText=obj["action_short"].as<String>();doneText=obj["done_when_short"].as<String>();nextText=obj["next_step_short"]|"";state="READY";
  if(!persist()){goalText=oldGoal;commandId=oldCommand;cycleId=oldCycle;actionText=oldAction;doneText=oldDone;nextText=oldNext;state=oldState;revision=oldRevision;dayIndex=oldDay;if(added){cards[selected]=Card();cardCount--;selectCard(previous);}error("persist_failed");return;}
  timeTrusted=false;render();offerAck();}
void sendHostEventAck(uint32_t seq){JsonDocument ack;ack["type"]="event_ack";ack["device_id"]=deviceId;ack["command_id"]=commandId;ack["cycle_id"]=cycleId;ack["revision"]=revision;ack["seq"]=seq;ack["persisted"]=true;ack["state"]=state;sendJson(ack);}
void handleHostEvent(JsonObject obj){static const char* keys[]={"type","protocol","command_id","cycle_id","revision","day_index","seq","event_type"};if(!onlyKeys(obj,keys,8)||obj["protocol"].as<int>()!=1||obj["cycle_id"].as<String>()!=cycleId||obj["command_id"].as<String>()!=commandId||(uint32_t)(obj["revision"]|0)!=revision){error("invalid_event");return;}uint32_t seq=obj["seq"]|0;String event=obj["event_type"]|"";if(seq<=lastHostSeq){sendHostEventAck(seq);return;}if(seq!=lastHostSeq+1||(event!="complete"&&event!="seal")){error("event_sequence");return;}bool doneToday=completedDay==dayIndex;if(event=="complete"&&(!timeTrusted||doneToday||state=="SEALED")){error(!timeTrusted?"time_untrusted":(doneToday?"already_done":"already_sealed"));return;}if(event=="seal"&&state=="SEALED"){error("already_sealed");return;}String oldState=state;uint32_t oldSeq=lastHostSeq,oldCompletedDay=completedDay;if(event=="complete"){state="DONE";completedDay=dayIndex;}else state="SEALED";lastHostSeq=seq;if(!persist()){state=oldState;lastHostSeq=oldSeq;completedDay=oldCompletedDay;error("persist_failed");return;}render();sendHostEventAck(seq);}
void sendPendingDeviceEvents(){JsonDocument queue;if(deserializeJson(queue,pendingDeviceEvents)||!queue.is<JsonArray>())return;for(JsonObject item:queue.as<JsonArray>()){JsonDocument doc;doc["type"]="event";doc["protocol"]=1;doc["device_id"]=deviceId;doc["seq"]=item["seq"];doc["command_id"]=item["command_id"];doc["cycle_id"]=item["cycle_id"];doc["revision"]=item["revision"];doc["day_index"]=item["day_index"];doc["event_type"]=item["type"];doc["status"]=item["status"];doc["pending_sync"]=true;sendJson(doc);}}
void handleFrame(const String& wire){JsonDocument doc;DeserializationError parse=deserializeJson(doc,wire);if(parse||!doc.is<JsonObject>()){error("invalid_json");return;}JsonObject obj=doc.as<JsonObject>();String type=obj["type"]|"";if(type!="offer"){String requested=obj["cycle_id"]|"";if(!requested.isEmpty()){int found=findCard(requested);if(found<0){if(type=="query"){JsonDocument missing;missing["type"]="status";missing["protocol"]=1;missing["device_id"]=deviceId;missing["cycle_id"]=requested;missing["state"]="MISSING";missing["persisted"]=false;missing["last_seq"]=0;sendJson(missing);}else error("cycle_missing");return;}selectCard(found);}}if(type=="offer")handleOffer(obj);else if(type=="event")handleHostEvent(obj);else if(type=="event_ack"){JsonDocument queue;if(deserializeJson(queue,pendingDeviceEvents)||!queue.is<JsonArray>()||queue.as<JsonArray>().size()==0){error("event_ack_sequence");return;}JsonObject first=queue.as<JsonArray>()[0];if(obj["cycle_id"].as<String>()!=first["cycle_id"].as<String>()||obj["command_id"].as<String>()!=first["command_id"].as<String>()||(uint32_t)(obj["revision"]|0)!=(uint32_t)(first["revision"]|0)||(uint32_t)(obj["seq"]|0)!=(uint32_t)(first["seq"]|0)){error("invalid_event_ack");return;}String old=pendingDeviceEvents;JsonDocument remaining;JsonArray next=remaining.to<JsonArray>();for(size_t i=1;i<queue.as<JsonArray>().size();i++)next.add(queue.as<JsonArray>()[i]);serializeJson(remaining,pendingDeviceEvents);if(!persist()){pendingDeviceEvents=old;error("persist_failed");return;}sendPendingDeviceEvents();}else if(type=="query"){JsonDocument status;status["type"]="status";status["protocol"]=1;status["device_id"]=deviceId;status["command_id"]=commandId;status["cycle_id"]=cycleId;status["revision"]=revision;status["persisted"]=!cycleId.isEmpty();status["state"]=state;status["last_seq"]=deviceSeq;sendJson(status);sendPendingDeviceEvents();}else if(type=="set_time"){bool valid=obj["protocol"].as<int>()==1&&obj["source"].as<String>()=="host_confirmed"&&obj["cycle_id"].as<String>()==cycleId&&obj["command_id"].as<String>()==commandId&&(uint64_t)(obj["utc_epoch"]|0)>1700000000ULL;timeTrusted=valid;if(!valid)error("time_source");else{JsonDocument ack;ack["type"]="time_ack";ack["command_id"]=commandId;ack["cycle_id"]=cycleId;ack["trusted"]=true;sendJson(ack);render();}}else error("unknown_type");}

void recordPhysical(const char* event){if(cardCount==0){error("no_commitment");return;}bool isComplete=strcmp(event,"complete")==0,doneToday=completedDay==dayIndex;if(isComplete&&(!timeTrusted||doneToday||state=="SEALED")){error(!timeTrusted?"time_untrusted":(doneToday?"already_done":"already_sealed"));return;}if(!isComplete&&state=="SEALED"){error("already_sealed");return;}JsonDocument queue;if(deserializeJson(queue,pendingDeviceEvents)||!queue.is<JsonArray>())queue.to<JsonArray>();if(queue.as<JsonArray>().size()>=8){error("event_queue_full");return;}String oldState=state,oldPending=pendingDeviceEvents;uint32_t oldSeq=deviceSeq,oldCompletedDay=completedDay;state=isComplete?"DONE":"SEALED";if(isComplete)completedDay=dayIndex;deviceSeq++;JsonObject item=queue.as<JsonArray>().add<JsonObject>();item["seq"]=deviceSeq;item["type"]=event;item["command_id"]=commandId;item["cycle_id"]=cycleId;item["revision"]=revision;item["day_index"]=dayIndex;item["status"]=state;serializeJson(queue,pendingDeviceEvents);if(!persist()){state=oldState;pendingDeviceEvents=oldPending;deviceSeq=oldSeq;completedDay=oldCompletedDay;error("persist_failed");return;}render();sendPendingDeviceEvents();}
void updateButtons(){bool a=M5.BtnA.isPressed(),b=M5.BtnB.isPressed();uint32_t now=millis();if(!operationOpen){if(a&&b){if(!bothSince)bothSince=now;if(now-bothSince>=kUnlockMs){operationOpen=true;operationOpenedAt=now;awaitRelease=true;chooseSeal=false;bothSince=0;render();}}else{bothSince=0;if(M5.BtnA.wasClicked()&&!b&&cardCount>1){selectCard((selected+1)%cardCount);render();}}return;}if(now-operationOpenedAt>15000){operationOpen=false;awaitRelease=false;confirmSince=0;render();return;}if(awaitRelease){if(!a&&!b)awaitRelease=false;return;}if(M5.BtnA.wasClicked()){chooseSeal=!chooseSeal;render();}if(b){if(!confirmSince)confirmSince=now;if(now-confirmSince>=kConfirmMs){recordPhysical(chooseSeal?"seal":"complete");operationOpen=false;confirmSince=0;}}else confirmSince=0;}
void handleFrameWithHandshake(const String& wire){JsonDocument doc;if(!deserializeJson(doc,wire)&&doc["type"].as<String>()=="hello_request"){JsonDocument hello;hello["type"]="hello";hello["protocol"]=1;hello["device_id"]=deviceId;hello["last_seq"]=deviceSeq;hello["multi_cycle"]=true;hello["capacity"]=kCapacity;hello["cycle_count"]=cardCount;sendJson(hello);return;}handleFrame(wire);}
}

void setup(){auto config=M5.config();M5.begin(config);Serial.begin(115200);store.begin("tenfold",false,"tenfold_data");uint64_t mac=ESP.getEfuseMac();deviceId="m5sticks3-"+String((uint32_t)(mac>>32),HEX)+String((uint32_t)mac,HEX);restore();if(cardCount==0&&snapshotVersion==0){store.end();store.begin("tenfold",true);restore();store.end();store.begin("tenfold",false,"tenfold_data");snapshotVersion=0;if(cardCount&&!persist())error("migration_persist_failed");}render();JsonDocument hello;hello["type"]="hello";hello["protocol"]=1;hello["device_id"]=deviceId;hello["last_seq"]=deviceSeq;hello["multi_cycle"]=true;hello["capacity"]=kCapacity;hello["cycle_count"]=cardCount;sendJson(hello);}
void loop(){static bool discardFrame=false;M5.update();updateButtons();while(Serial.available()){char c=(char)Serial.read();if(c=='\n'){if(!discardFrame&&!serialLine.isEmpty())handleFrameWithHandshake(serialLine);serialLine="";discardFrame=false;}else if(c!='\r'&&!discardFrame){if(serialLine.length()>=kMaxFrame){serialLine="";discardFrame=true;error("too_large");}else serialLine+=c;}}delay(5);}
