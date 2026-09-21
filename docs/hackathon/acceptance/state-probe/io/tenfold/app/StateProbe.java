package io.tenfold.app;
import android.content.SharedPreferences;
import java.util.*;

/** Runs the unmodified production CycleState against an Android-like memory/disk stub. */
public class StateProbe {
  static class Memory implements SharedPreferences {
    Map<String,Object> ram=new HashMap<>(),disk=new HashMap<>(); boolean fail;
    public Map<String,?> getAll(){return new HashMap<>(ram);}
    public String getString(String k,String d){return (String)ram.getOrDefault(k,d);}
    public int getInt(String k,int d){return (Integer)ram.getOrDefault(k,d);}
    public boolean getBoolean(String k,boolean d){return (Boolean)ram.getOrDefault(k,d);}
    public Editor edit(){return new Editor(){
      Map<String,Object> pending=new HashMap<>();
      Set<String> removed=new HashSet<>();
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
    Memory m=new Memory();CycleState c=create(m);
    c.seal("old note","old recovery");m.edit().putInt("device_seq",7).putString("protocol_outbox","old pending").commit();c.createCycle("new goal","new stuck","new action","new done");
    report("CS01_NEW_CYCLE_STALE",c.stopNote().equals("old note")&&c.recoveryCard().equals("old recovery")&&m.getInt("device_seq",0)==7,"internal createCycle retains prior fields; current UI has no restart-cycle entry");
    m=new Memory();c=create(m);c.advanceDemoDay();c.resumeExisting();c.chooseMode(CycleState.MODE_USB);
    report("CS02_DEMO_PROMOTED_TO_REAL",c.day()==2&&c.phase().equals(CycleState.PHASE_ACTIVE),"UI sequence: demo next day, confirm resume, home switch USB retains demo day/state");
    m=new Memory();c=create(m);c.completePhone();c.advanceDemoDay();boolean before=c.canComplete();c.completePhone();
    report("CS03_NEXT_UNCONFIRMED_COMPLETE",before&&c.completed(),"internal API bypass; home routes NEXT to new-action screen so ordinary button not reachable");
    m=new Memory();c=create(m);m.fail=true;c.seal("must survive","next");boolean claimed=c.phoneSaved();m.restart();
    report("CS04_FAILED_SEAL_CLAIM",claimed&&!c.stopNote().equals("must survive"),"UI confirms saved despite failed disk write; restart loses note");
    m=new Memory();c=create(m);boolean accepted=c.acceptDeviceEvent(1,"complete");
    report("CS05_UNBOUND_DEVICE_EVENT",accepted&&c.completed(),"MainActivity passes only seq/type, no mode/cycle/command/revision validation");
    m=new Memory();c=create(m);m.edit().putString("cycle_start_date","2000-01-01").commit();c.chooseMode(CycleState.MODE_USB);
    report("CS06_REAL_DATE_UNUSED",c.day()==1&&c.phase().equals(CycleState.PHASE_ACTIVE),"real date has no transition or cycle-end processing");
  }
}
