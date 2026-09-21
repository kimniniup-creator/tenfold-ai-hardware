package io.tenfold.app;

import android.content.SharedPreferences;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.temporal.ChronoUnit;
import java.util.Map;
import java.util.UUID;

/** Durable cycle repository. A method returns true only after synchronous SharedPreferences commit. */
final class CycleState {
  static final String MODE_SIMULATED="SIMULATED",MODE_USB="USB";
  static final String PHASE_ACTIVE="ACTIVE",PHASE_DONE="DONE",PHASE_SEALED="SEALED";
  static final String PHASE_RESUME="RESUME_AVAILABLE",PHASE_NEXT="AWAITING_NEXT_ACTION",PHASE_REVIEW="CYCLE_REVIEW";
  private final SharedPreferences prefs;
  CycleState(SharedPreferences prefs){this.prefs=prefs;}
  boolean hasCycle(){return !text("action").isEmpty();}
  String text(String key){return prefs.getString(key,"");}
  String phase(){return prefs.getString("phase",PHASE_ACTIVE);}
  String mode(){return prefs.getString("mode",MODE_SIMULATED);}
  boolean isSimulated(){return MODE_SIMULATED.equals(mode());}
  boolean completed(){return prefs.getBoolean("completed",false);}
  int day(){return Math.max(1,Math.min(10,prefs.getInt(isSimulated()?"demo_day":"day_index",1)));}
  String commandId(){return text("command_id");}
  boolean deviceSaved(){return prefs.getBoolean("device_saved",false);}
  String stopNote(){return text("stop_note");}
  String recoveryCard(){String value=text("recovery_card");return value.isEmpty()?text("action"):value;}

  boolean createCycle(String goal,String stuck,String action,String done){
    String today=LocalDate.now(ZoneId.systemDefault()).toString();
    SharedPreferences.Editor edit=prefs.edit();
    String[] stale={"stop_note","recovery_card","protocol_outbox","device_seq","device_event_history","host_seq_counter","completed","device_saved","phone_saved","demo_day","day_index","command_id","cycle_id","revision","phase"};
    for(String key:stale)edit.remove(key);
    for(int day=1;day<=10;day++){edit.remove("day_"+day+"_status").remove("day_"+day+"_date").remove("day_"+day+"_action").remove("day_"+day+"_done").remove("day_"+day+"_note").remove("day_"+day+"_next");}
    return commit(edit.putString("goal",goal).putString("stuck",stuck).putString("action",action).putString("done",done)
      .putString("phase",PHASE_ACTIVE).putString("mode",MODE_SIMULATED).putString("cycle_id",UUID.randomUUID().toString())
      .putString("command_id",UUID.randomUUID().toString()).putString("cycle_start_date",today)
      .putString("tz",ZoneId.systemDefault().getId()).putInt("revision",1).putInt("demo_day",1).putInt("day_index",1)
      .putBoolean("completed",false).putBoolean("phone_saved",true).putBoolean("device_saved",false));
  }

  /** Explicitly exits demo history and starts a fresh real day-one cycle with the confirmed text. */
  boolean startRealFromConfirmedCard(){
    return commit(prefs.edit().putString("mode",MODE_USB).putInt("day_index",1).putBoolean("completed",false)
      .putString("phase",PHASE_ACTIVE).putString("stop_note","").putString("recovery_card",text("action"))
      .putString("cycle_id",UUID.randomUUID().toString()).putString("command_id",UUID.randomUUID().toString())
      .putString("cycle_start_date",LocalDate.now(ZoneId.systemDefault()).toString()).putString("tz",ZoneId.systemDefault().getId())
      .putInt("revision",1).putBoolean("device_saved",false).remove("protocol_outbox").remove("host_seq_counter").remove("device_seq").remove("device_event_history"));
  }
  boolean markPending(){return commit(prefs.edit().putBoolean("device_saved",false));}
  boolean acceptDeviceAck(String command,String cycle,int revision){if(!command.equals(commandId())||!cycle.equals(text("cycle_id"))||revision!=prefs.getInt("revision",1))return false;return commit(prefs.edit().putBoolean("device_saved",true));}
  boolean acceptDeviceEvent(String device,String command,String cycle,int revision,int seq,String eventType){
    if(isSimulated()||device.isEmpty()||!cycle.equals(text("cycle_id"))||revision<1||revision>prefs.getInt("revision",1))return false;
    int last=prefs.getInt("device_seq",0);if(seq<=last)return true;if(seq!=last+1)return false;
    if(!"complete".equals(eventType)&&!"seal".equals(eventType))return false;
    boolean current=revision==prefs.getInt("revision",1)&&command.equals(commandId());
    String history=prefs.getString("device_event_history","")+seq+"|"+revision+"|"+command+"|"+eventType+"\n";
    SharedPreferences.Editor edit=prefs.edit().putInt("device_seq",seq).putString("device_event_history",history);
    if(current&&"complete".equals(eventType))edit.putBoolean("completed",true).putString("phase",PHASE_DONE);
    else if(current)edit.putString("phase",PHASE_SEALED);
    return commit(edit);
  }
  boolean completePhone(){return canComplete()&&commit(recordEditor("COMPLETED","",recoveryCard()).putBoolean("completed",true).putString("phase",PHASE_DONE));}
  boolean canComplete(){return PHASE_ACTIVE.equals(phase())&&!completed();}
  boolean seal(String note,String recovery){String status=completed()?"COMPLETED_SEALED":"SEALED_UNFINISHED";String next=recovery.isEmpty()?text("action"):recovery;return commit(recordEditor(status,note,next).putString("phase",PHASE_SEALED).putString("stop_note",note).putString("recovery_card",next).putBoolean("phone_saved",true));}
  boolean advanceDemoDay(){if(!isSimulated())return false;if(day()>=10)return commit(prefs.edit().putString("phase",PHASE_REVIEW));boolean wasDone=completed();return commit(prefs.edit().putInt("demo_day",day()+1).putBoolean("completed",false).putBoolean("device_saved",false).putString("phase",wasDone?PHASE_NEXT:PHASE_RESUME));}
  boolean refreshRealDate(){
    if(isSimulated()||!hasCycle())return true;
    try{ZoneId zone=ZoneId.of(text("tz"));long slot=ChronoUnit.DAYS.between(LocalDate.parse(text("cycle_start_date")),LocalDate.now(zone))+1;if(slot<=day())return true;if(slot>10)return commit(prefs.edit().putString("phase",PHASE_REVIEW));boolean wasDone=completed();return commit(prefs.edit().putInt("day_index",(int)slot).putBoolean("completed",false).putBoolean("device_saved",false).putString("phase",wasDone?PHASE_NEXT:PHASE_RESUME));}catch(Exception error){return false;}
  }
  boolean resumeExisting(){return commit(prefs.edit().putString("action",recoveryCard()).putString("done","完成这一步并留下可验证结果").putString("phase",PHASE_ACTIVE).putInt("revision",prefs.getInt("revision",1)+1).putString("command_id",UUID.randomUUID().toString()).putBoolean("device_saved",false));}
  boolean confirmNewAction(String action,String done){return commit(prefs.edit().putString("action",action).putString("done",done).putString("phase",PHASE_ACTIVE).putInt("revision",prefs.getInt("revision",1)+1).putString("command_id",UUID.randomUUID().toString()).putBoolean("device_saved",false));}
  String reviewSummary(){StringBuilder result=new StringBuilder();for(int day=1;day<=10;day++){String status=prefs.getString("day_"+day+"_status","");result.append("第 ").append(day).append(" 天 · ").append(status.isEmpty()?"无记录":status).append('\n');String action=prefs.getString("day_"+day+"_action","");if(!action.isEmpty())result.append(action).append('\n');String note=prefs.getString("day_"+day+"_note","");if(!note.isEmpty())result.append("停在：").append(note).append('\n');result.append('\n');}return result.toString();}
  boolean hasArchive(){return !prefs.getString("archived_summary","").isEmpty();}
  String archivedSummary(){return prefs.getString("archived_summary","");}
  boolean archive(){SharedPreferences.Editor edit=prefs.edit().putString("archived_summary",text("goal")+"\n\n"+reviewSummary()).putString("archived_cycle_id",text("cycle_id"));String[] active={"goal","stuck","action","done","stop_note","recovery_card","phase","mode","cycle_id","command_id","cycle_start_date","tz","revision","demo_day","day_index","completed","device_saved","phone_saved","protocol_outbox","device_seq","device_event_history","host_seq_counter"};for(String key:active)edit.remove(key);for(int day=1;day<=10;day++)edit.remove("day_"+day+"_status").remove("day_"+day+"_date").remove("day_"+day+"_action").remove("day_"+day+"_done").remove("day_"+day+"_note").remove("day_"+day+"_next");return commit(edit);}
  private SharedPreferences.Editor recordEditor(String status,String note,String next){String prefix="day_"+day()+"_";String date;try{date=LocalDate.parse(text("cycle_start_date")).plusDays(day()-1L).toString();}catch(Exception ignored){date="";}return prefs.edit().putString(prefix+"status",status).putString(prefix+"date",date).putString(prefix+"action",text("action")).putString(prefix+"done",text("done")).putString(prefix+"note",note).putString(prefix+"next",next);}
  private boolean commit(SharedPreferences.Editor edit){
    Map<String,?> before=prefs.getAll();if(edit.commit())return true;
    SharedPreferences.Editor rollback=prefs.edit().clear();
    for(Map.Entry<String,?> entry:before.entrySet()){Object value=entry.getValue();if(value instanceof String)rollback.putString(entry.getKey(),(String)value);else if(value instanceof Integer)rollback.putInt(entry.getKey(),(Integer)value);else if(value instanceof Boolean)rollback.putBoolean(entry.getKey(),(Boolean)value);else if(value instanceof Long)rollback.putLong(entry.getKey(),(Long)value);else if(value instanceof Float)rollback.putFloat(entry.getKey(),(Float)value);}
    rollback.commit();return false;
  }
}
