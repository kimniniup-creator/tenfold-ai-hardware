package io.tenfold.app;

import android.content.SharedPreferences;
import java.time.LocalDate;
import java.time.ZoneId;
import org.json.JSONObject;

final class DeviceProtocol {
  static JSONObject offer(SharedPreferences p) {
    JSONObject value=new JSONObject();
    put(value,"type","offer"); put(value,"protocol",1); put(value,"command_id",p.getString("command_id",""));
    put(value,"cycle_id",p.getString("cycle_id","")); put(value,"revision",p.getInt("revision",1));
    int day=p.getInt("demo_day",1);String start=p.getString("cycle_start_date","");String tz=p.getString("tz",ZoneId.systemDefault().getId());
    String localDate=start;try{localDate=CycleState.MODE_SIMULATED.equals(p.getString("mode",CycleState.MODE_SIMULATED))?LocalDate.parse(start).plusDays(day-1L).toString():LocalDate.now(ZoneId.of(tz)).toString();}catch(Exception ignored){}
    put(value,"day_index",day); put(value,"cycle_start_date",start);
    put(value,"local_date",localDate); put(value,"tz",tz);
    put(value,"action_short",shortText(p.getString("action",""))); put(value,"done_when_short",shortText(p.getString("done","")));
    put(value,"stop_at",p.getString("stop_at","22:00")); put(value,"next_step_short",shortText(p.getString("recovery_card",p.getString("action",""))));
    return value;
  }
  static JSONObject query(SharedPreferences p) {JSONObject value=new JSONObject();put(value,"type","query");put(value,"command_id",p.getString("command_id",""));put(value,"cycle_id",p.getString("cycle_id",""));return value;}
  static JSONObject event(SharedPreferences p,String eventType,int seq) {JSONObject value=new JSONObject();put(value,"type","event");put(value,"protocol",1);put(value,"command_id",p.getString("command_id",""));put(value,"cycle_id",p.getString("cycle_id",""));put(value,"revision",p.getInt("revision",1));put(value,"day_index",p.getInt("demo_day",1));put(value,"seq",seq);put(value,"event_type",eventType);return value;}
  static JSONObject eventAck(int seq) {JSONObject value=new JSONObject();put(value,"type","event_ack");put(value,"seq",seq);put(value,"persisted",true);return value;}
  private static void put(JSONObject value,String key,Object item){try{value.put(key,item);}catch(Exception error){throw new IllegalStateException("JSON_BUILD_"+key,error);}}
  private static String shortText(String value){String text=value.trim();int count=text.codePointCount(0,text.length());return count>24?text.substring(0,text.offsetByCodePoints(0,24)):text;}
}
