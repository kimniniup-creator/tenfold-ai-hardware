package io.tenfold.app;

import android.content.SharedPreferences;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.temporal.ChronoUnit;
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
    String[] stale={"stop_note","recovery_card","protocol_outbox","device_seq","host_seq_counter","completed","device_saved","phone_saved","demo_day","day_index","command_id","cycle_id","revision","phase"};
    for(String key:stale)edit.remove(key);
    return edit.putString("goal",goal).putString("stuck",stuck).putString("action",action).putString("done",done)
      .putString("phase",PHASE_ACTIVE).putString("mode",MODE_SIMULATED).putString("cycle_id",UUID.randomUUID().toString())
      .putString("command_id",UUID.randomUUID().toString()).putString("cycle_start_date",today)
      .putString("tz",ZoneId.systemDefault().getId()).putInt("revision",1).putInt("demo_day",1).putInt("day_index",1)
      .putBoolean("completed",false).putBoolean("phone_saved",true).putBoolean("device_saved",false).commit();
  }

  /** Explicitly exits demo history and starts a fresh real day-one cycle with the confirmed text. */
  boolean startRealFromConfirmedCard(){
    return prefs.edit().putString("mode",MODE_USB).putInt("day_index",1).putBoolean("completed",false)
      .putString("phase",PHASE_ACTIVE).putString("stop_note","").putString("recovery_card",text("action"))
      .putString("cycle_id",UUID.randomUUID().toString()).putString("command_id",UUID.randomUUID().toString())
      .putString("cycle_start_date",LocalDate.now(ZoneId.systemDefault()).toString()).putString("tz",ZoneId.systemDefault().getId())
      .putInt("revision",1).putBoolean("device_saved",false).remove("protocol_outbox").remove("host_seq_counter").remove("device_seq").commit();
  }
  boolean markPending(){return prefs.edit().putBoolean("device_saved",false).commit();}
  boolean acceptDeviceAck(String command,String cycle,int revision){if(!command.equals(commandId())||!cycle.equals(text("cycle_id"))||revision!=prefs.getInt("revision",1))return false;return prefs.edit().putBoolean("device_saved",true).commit();}
  boolean acceptDeviceEvent(String device,String command,String cycle,int revision,int seq,String eventType){
    if(isSimulated()||device.isEmpty()||!command.equals(commandId())||!cycle.equals(text("cycle_id"))||revision!=prefs.getInt("revision",1))return false;
    int last=prefs.getInt("device_seq",0);if(seq<=last)return true;if(seq!=last+1)return false;
    SharedPreferences.Editor edit=prefs.edit().putInt("device_seq",seq);
    if("complete".equals(eventType))edit.putBoolean("completed",true).putString("phase",PHASE_DONE);
    else if("seal".equals(eventType))edit.putString("phase",PHASE_SEALED);else return false;
    return edit.commit();
  }
  boolean completePhone(){return canComplete()&&prefs.edit().putBoolean("completed",true).putString("phase",PHASE_DONE).commit();}
  boolean canComplete(){return PHASE_ACTIVE.equals(phase())&&!completed();}
  boolean seal(String note,String recovery){return prefs.edit().putString("phase",PHASE_SEALED).putString("stop_note",note).putString("recovery_card",recovery.isEmpty()?text("action"):recovery).putBoolean("phone_saved",true).commit();}
  boolean advanceDemoDay(){if(!isSimulated())return false;if(day()>=10)return prefs.edit().putString("phase",PHASE_REVIEW).commit();boolean wasDone=completed();return prefs.edit().putInt("demo_day",day()+1).putBoolean("completed",false).putBoolean("device_saved",false).putString("phase",wasDone?PHASE_NEXT:PHASE_RESUME).commit();}
  boolean refreshRealDate(){
    if(isSimulated()||!hasCycle())return true;
    try{ZoneId zone=ZoneId.of(text("tz"));long slot=ChronoUnit.DAYS.between(LocalDate.parse(text("cycle_start_date")),LocalDate.now(zone))+1;if(slot<=day())return true;if(slot>10)return prefs.edit().putString("phase",PHASE_REVIEW).commit();boolean wasDone=completed();return prefs.edit().putInt("day_index",(int)slot).putBoolean("completed",false).putBoolean("device_saved",false).putString("phase",wasDone?PHASE_NEXT:PHASE_RESUME).commit();}catch(Exception error){return false;}
  }
  boolean resumeExisting(){return prefs.edit().putString("phase",PHASE_ACTIVE).commit();}
  boolean confirmNewAction(String action,String done){return prefs.edit().putString("action",action).putString("done",done).putString("phase",PHASE_ACTIVE).putInt("revision",prefs.getInt("revision",1)+1).putString("command_id",UUID.randomUUID().toString()).putBoolean("device_saved",false).commit();}
}
