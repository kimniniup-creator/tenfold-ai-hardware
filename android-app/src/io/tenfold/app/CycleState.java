package io.tenfold.app;

import android.content.SharedPreferences;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.UUID;

/** Durable phone facts. USB writes never become device facts until a matching ACK arrives. */
final class CycleState {
  static final String MODE_SIMULATED = "SIMULATED";
  static final String MODE_USB = "USB";
  static final String PHASE_ACTIVE = "ACTIVE";
  static final String PHASE_DONE = "DONE";
  static final String PHASE_SEALED = "SEALED";
  static final String PHASE_RESUME = "RESUME_AVAILABLE";
  static final String PHASE_NEXT = "AWAITING_NEXT_ACTION";
  static final String PHASE_REVIEW = "CYCLE_REVIEW";

  private final SharedPreferences prefs;

  CycleState(SharedPreferences prefs) { this.prefs = prefs; }
  boolean hasCycle() { return !text("action").isEmpty(); }
  String text(String key) { return prefs.getString(key, ""); }
  String phase() { return prefs.getString("phase", PHASE_ACTIVE); }
  String mode() { return prefs.getString("mode", MODE_SIMULATED); }
  boolean isSimulated() { return MODE_SIMULATED.equals(mode()); }
  boolean completed() { return prefs.getBoolean("completed", false); }
  int day() { return Math.max(1, Math.min(10, prefs.getInt("demo_day", 1))); }
  String commandId() { return text("command_id"); }
  boolean deviceSaved() { return prefs.getBoolean("device_saved", false); }
  boolean phoneSaved() { return prefs.getBoolean("phone_saved", false); }
  String stopNote() { return text("stop_note"); }
  String recoveryCard() { String value=text("recovery_card"); return value.isEmpty()?text("action"):value; }

  void createCycle(String goal, String stuck, String action, String done) {
    String today=LocalDate.now(ZoneId.systemDefault()).toString();
    prefs.edit().putString("goal",goal).putString("stuck",stuck).putString("action",action)
      .putString("done",done).putString("phase",PHASE_ACTIVE).putString("mode",MODE_SIMULATED)
      .putString("cycle_id",UUID.randomUUID().toString()).putString("command_id",UUID.randomUUID().toString())
      .putString("cycle_start_date",today).putString("tz",ZoneId.systemDefault().getId())
      .putInt("revision",1).putInt("demo_day",1).putBoolean("completed",false)
      .putBoolean("phone_saved",true).putBoolean("device_saved",false).commit();
  }

  void chooseMode(String mode) { prefs.edit().putString("mode",mode).putBoolean("device_saved",false).commit(); }
  void markPending(String commandId) { prefs.edit().putString("command_id",commandId).putBoolean("device_saved",false).commit(); }
  boolean acceptDeviceAck(String commandId, String cycleId, int revision) {
    if (!commandId.equals(commandId()) || !cycleId.equals(text("cycle_id")) || revision != prefs.getInt("revision",1)) return false;
    return prefs.edit().putBoolean("device_saved",true).commit();
  }
  boolean acceptDeviceEvent(int seq,String eventType) {
    int last=prefs.getInt("device_seq",0);if(seq<=last)return true;if(seq!=last+1)return false;
    SharedPreferences.Editor edit=prefs.edit().putInt("device_seq",seq);
    if("complete".equals(eventType))edit.putBoolean("completed",true).putString("phase",PHASE_DONE);
    else if("seal".equals(eventType))edit.putString("phase",PHASE_SEALED);else return false;
    return edit.commit();
  }
  void completePhone() { if (canComplete()) prefs.edit().putBoolean("completed",true).putString("phase",PHASE_DONE).commit(); }
  boolean canComplete() { return !completed() && !PHASE_SEALED.equals(phase()) && !PHASE_REVIEW.equals(phase()); }
  void seal(String note, String recovery) {
    prefs.edit().putString("phase",PHASE_SEALED).putString("stop_note",note)
      .putString("recovery_card",recovery.isEmpty()?text("action"):recovery).putBoolean("phone_saved",true).commit();
  }
  void advanceDemoDay() {
    if (!isSimulated()) return;
    if (day() >= 10) { prefs.edit().putString("phase",PHASE_REVIEW).commit(); return; }
    boolean wasDone=completed();
    prefs.edit().putInt("demo_day",day()+1).putBoolean("completed",false).putBoolean("device_saved",false)
      .putString("phase",wasDone?PHASE_NEXT:PHASE_RESUME).commit();
  }
  void resumeExisting() { prefs.edit().putString("phase",PHASE_ACTIVE).commit(); }
  void confirmNewAction(String action, String done) {
    prefs.edit().putString("action",action).putString("done",done).putString("phase",PHASE_ACTIVE)
      .putInt("revision",prefs.getInt("revision",1)+1).putString("command_id",UUID.randomUUID().toString())
      .putBoolean("device_saved",false).commit();
  }
}
