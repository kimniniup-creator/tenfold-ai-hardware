package io.tenfold.app;

import android.content.SharedPreferences;
import org.json.JSONArray;
import org.json.JSONObject;

/** Persisted FIFO for host events. Sequence is assigned once and survives reconnects. */
final class ProtocolOutbox {
  private final SharedPreferences prefs;
  ProtocolOutbox(SharedPreferences prefs){this.prefs=prefs;}
  synchronized JSONObject enqueue(String type){
    int seq=prefs.getInt("host_seq_counter",0)+1;JSONObject frame=DeviceProtocol.event(prefs,type,seq);
    JSONArray queue=read();queue.put(frame);boolean ok=prefs.edit().putInt("host_seq_counter",seq).putString("protocol_outbox",queue.toString()).commit();
    if(!ok)throw new IllegalStateException("OUTBOX_COMMIT_FAILED");return frame;
  }
  synchronized JSONObject peek(){JSONArray queue=read();return queue.length()==0?null:queue.optJSONObject(0);}
  synchronized boolean acknowledge(int seq){JSONArray queue=read();JSONObject first=queue.optJSONObject(0);if(first==null||first.optInt("seq",-1)!=seq)return false;JSONArray next=new JSONArray();for(int i=1;i<queue.length();i++)next.put(queue.opt(i));return prefs.edit().putString("protocol_outbox",next.toString()).commit();}
  private JSONArray read(){try{return new JSONArray(prefs.getString("protocol_outbox","[]"));}catch(Exception ignored){return new JSONArray();}}
}
