package io.tenfold.app;
import android.content.SharedPreferences;
import java.util.*;
import java.time.*;
public class StateProbeV2 {
  static class Memory implements SharedPreferences {
    Map<String,Object> ram=new HashMap<>(),disk=new HashMap<>(); boolean fail;
    public Map<String,?> getAll(){return new HashMap<>(ram);}
    public String getString(String k,String d){return (String)ram.getOrDefault(k,d);}
    public int getInt(String k,int d){return (Integer)ram.getOrDefault(k,d);}
    public boolean getBoolean(String k,boolean d){return (Boolean)ram.getOrDefault(k,d);}
    public Editor edit(){return new Editor(){
      Map<String,Object> pending=new HashMap<>();Set<String> removed=new HashSet<>();
      boolean cleared;
      public Editor clear(){cleared=true;return this;}
      public Editor putLong(String k,long v){pending.put(k,v);return this;}
      public Editor putFloat(String k,float v){pending.put(k,v);return this;}
      public Editor remove(String k){removed.add(k);return this;}
      public Editor putString(String k,String v){pending.put(k,v);return this;}
      public Editor putInt(String k,int v){pending.put(k,v);return this;}
      public Editor putBoolean(String k,boolean v){pending.put(k,v);return this;}
      public boolean commit(){if(cleared)ram.clear();removed.forEach(ram::remove);ram.putAll(pending);if(fail)return false;if(cleared)disk.clear();removed.forEach(disk::remove);disk.putAll(pending);return true;}
    };}
    void restart(){ram=new HashMap<>(disk);}
  }
  static void report(String id,boolean defect,String details){System.out.println(id+"="+(defect?"REPRODUCED":"NOT_REPRODUCED")+" | "+details);}
  static CycleState create(Memory m){CycleState c=new CycleState(m);c.createCycle("goal","stuck","action","done");return c;}
  public static void main(String[] args){
    Memory m=new Memory();CycleState c=create(m);c.seal("old note","old recovery");m.edit().putInt("device_seq",7).putString("protocol_outbox","old pending").commit();c.createCycle("new goal","new stuck","new action","new done");
    report("CS01_NEW_CYCLE_STALE",!c.stopNote().isEmpty()||c.recoveryCard().equals("old recovery")||m.getInt("device_seq",0)!=0||!m.getString("protocol_outbox","").isEmpty(),"old fields cleared");
    m=new Memory();c=create(m);String oldCycle=c.text("cycle_id");c.advanceDemoDay();c.resumeExisting();c.startRealFromConfirmedCard();
    report("CS02_DEMO_PROMOTED_TO_REAL",c.day()!=1||oldCycle.equals(c.text("cycle_id")),"explicit fresh real cycle day one");
    m=new Memory();c=create(m);c.completePhone();c.advanceDemoDay();boolean before=c.canComplete();c.completePhone();
    report("CS03_NEXT_UNCONFIRMED_COMPLETE",before||c.completed(),"ACTIVE-only complete guard");
    m=new Memory();c=create(m);m.fail=true;boolean saved=c.seal("must survive","next");
    report("CS04_FAILED_SEAL_CLAIM",saved,"method returns failure and MainActivity checks it");
    report("CS04B_FAILED_WRITE_RAM_MUTATION",c.phase().equals(CycleState.PHASE_SEALED)&&c.stopNote().equals("must survive"),"commit=false still changes Android memory; return-home can display unsaved SEALED");
    m=new Memory();c=create(m);boolean accepted=c.acceptDeviceEvent("m5sticks3-p0",c.commandId(),c.text("cycle_id"),1,1,"complete");c.startRealFromConfirmedCard();accepted|=c.acceptDeviceEvent("m5sticks3-p0","wrong","wrong",1,1,"complete");
    report("CS05_UNBOUND_DEVICE_EVENT",accepted||c.completed(),"simulation and wrong cycle/command rejected; session device check exists in MainActivity");
    m=new Memory();c=create(m);c.startRealFromConfirmedCard();m.edit().putString("cycle_start_date",LocalDate.now(ZoneId.of(c.text("tz"))).minusDays(1).toString()).commit();c.refreshRealDate();
    report("CS06_REAL_DATE_UNUSED",c.day()!=2||!c.phase().equals(CycleState.PHASE_RESUME),"next real day resumes unfinished card");
    c.resumeExisting();m.fail=true;boolean marked=c.completePhone();m.fail=false;boolean retry=c.completePhone();m.restart();
    report("CS07_COMPLETE_RETRY_LOST",!marked&&!retry&&!c.completed(),"failed commit sets RAM DONE so retry guard refuses; restart loses completion");
    m=new Memory();c=create(m);c.startRealFromConfirmedCard();m.fail=true;
    boolean persisted=c.acceptDeviceEvent("m5sticks3-p0",c.commandId(),c.text("cycle_id"),1,1,"complete");
    boolean sameCycle=true; // Exact accdbcb MainActivity fallback condition, not part of CycleState.
    report("ACK01_FAILED_EVENT_FALLBACK",!persisted&&(persisted||sameCycle),"accdbcb MainActivity current||sameCycle ACKs failed production acceptDeviceEvent");
    m=new Memory();c=create(m);c.startRealFromConfirmedCard();String firstCommand=c.commandId();String cycleId=c.text("cycle_id");c.confirmNewAction("new action","new done");
    boolean oldAccepted=c.acceptDeviceEvent("m5sticks3-p0",firstCommand,cycleId,1,1,"complete");
    boolean newAccepted=c.acceptDeviceEvent("m5sticks3-p0",c.commandId(),cycleId,2,2,"complete");
    report("ACK02_OLD_REV_CURSOR_GAP",!oldAccepted&&!newAccepted&&m.getInt("device_seq",0)==0,"accdbcb ACKs old seq1 without cursor then rejects and ACKs new seq2");
  }
}
