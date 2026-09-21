package io.tenfold.app;

import android.app.Activity;
import android.os.Bundle;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.text.InputType;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONObject;

/** Tenfold P0: one commitment, a truthful stop, and a concrete route back tomorrow. */
public final class MainActivity extends Activity implements UsbTransport.Listener {
  private SharedPreferences prefs;
  private CycleState cycle;
  private AgentClient agent;
  private UsbTransport usb;
  private ProtocolOutbox outbox;
  private LinearLayout body;
  private TextView liveStatus;
  private final int ink=Color.rgb(9,11,10), panel=Color.rgb(22,27,23), lime=Color.rgb(183,255,77);

  @Override public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    prefs=getSharedPreferences("tenfold",MODE_PRIVATE);
    cycle=new CycleState(prefs); agent=new AgentClient(prefs); outbox=new ProtocolOutbox(prefs); usb=new UsbTransport(this,this);
    showHome();
  }

  @Override protected void onDestroy(){usb.close();super.onDestroy();}

  private void page(String title,String meta){
    ScrollView scroll=new ScrollView(this); body=new LinearLayout(this); body.setOrientation(LinearLayout.VERTICAL);
    body.setPadding(28,30,28,30); body.setBackgroundColor(ink); scroll.addView(body); setContentView(scroll);
    label("TENFOLD / FIELD SYSTEM",11,lime); label(title,28,Color.WHITE);
    liveStatus=label(meta,13,Color.LTGRAY); liveStatus.setBackgroundColor(panel);
  }

  private TextView label(String text,int size,int color){
    TextView view=new TextView(this); view.setText(text); view.setTextSize(size); view.setTextColor(color);
    view.setPadding(14,14,14,14); body.addView(view); return view;
  }

  private EditText field(String label,String value){
    label(label.toUpperCase(),11,lime); EditText edit=new EditText(this); edit.setText(value);
    edit.setTextColor(Color.WHITE); edit.setHintTextColor(Color.GRAY); body.addView(edit); return edit;
  }

  private void button(String title,View.OnClickListener listener){
    Button button=new Button(this); button.setText(title); button.setAllCaps(false); button.setTextColor(Color.BLACK);
    button.setBackgroundColor(lime); button.setOnClickListener(listener); body.addView(button);
  }

  private String truthLine(){
    if(cycle.isSimulated())return "SIMULATED DEVICE · 手机本地演示，不声称硬件已收到";
    return cycle.deviceSaved()?"USB DEVICE · 设备已持久化 ACK":"USB DEVICE · 手机已保存 / 设备待确认";
  }

  private void showHome(){
    if(!cycle.hasCycle()){showSetup();return;}
    if(CycleState.PHASE_RESUME.equals(cycle.phase())){showResume();return;}
    if(CycleState.PHASE_NEXT.equals(cycle.phase())){showNewAction();return;}
    if(CycleState.PHASE_REVIEW.equals(cycle.phase())){showReview();return;}
    page("今天到这里，明天接得上。",truthLine()+"\n"+(cycle.isSimulated()?"DEMO TIME · DAY "+cycle.day()+" / 10":"REAL CYCLE · "+cycle.text("cycle_start_date")+" · "+cycle.text("tz")));
    label("TODAY\n"+cycle.text("action"),21,Color.WHITE);
    label("DONE WHEN\n"+cycle.text("done"),14,Color.LTGRAY);
    if(cycle.completed())label("PHONE FACT · 今日已完成并保存",14,lime);
    if(CycleState.PHASE_SEALED.equals(cycle.phase()))label("SEALED · "+cycle.recoveryCard(),14,lime);
    if(cycle.canComplete())button("确认：今天完成",v->completeToday());
    button("今天到这里",v->showSeal());
    if(cycle.isSimulated())button("DEMO TIME：进入下一天",v->{cycle.advanceDemoDay();showHome();});
    button(cycle.isSimulated()?"切换到真实 USB 设备":"重发同一张卡 / 查询 ACK",v->connectOrRetry());
    button("Agent 与隐私设置",v->showSettings());
  }

  private void showSetup(){
    page("建立唯一十日承诺。","手填始终可用 · Agent只提议，不自动激活");
    EditText goal=field("十日想交付什么","");
    EditText stuck=field("今天卡在哪","");
    EditText minutes=field("今晚剩余分钟（5–45）","12"); minutes.setInputType(InputType.TYPE_CLASS_NUMBER);
    EditText action=field("今天做到哪就够","");
    EditText done=field("完成条件","");
    button(agent.configured()?"让真实 Agent 提议停止边界":"用离线规则填一张候选卡",v->{
      int budget=clampMinutes(minutes.getText().toString());
      if(agent.configured())requestProposal(goal.getText().toString(),stuck.getText().toString(),budget,action,done,null);
      else {action.setText("用 "+budget+" 分钟验证："+stuck.getText().toString());done.setText("留下一个可复现结果和明天入口");liveStatus.setText("OFFLINE RULES · 没有发起 LLM 请求");}
    });
    button("确认并保存这张今日卡",v->{
      if(goal.length()==0||action.length()==0||done.length()==0){toast("十日结果、今日动作和完成条件必须确认");return;}
      cycle.createCycle(goal.getText().toString(),stuck.getText().toString(),action.getText().toString(),done.getText().toString());
      showHome();
    });
  }

  private void completeToday(){
    cycle.completePhone(); toast("完成事实已先保存到手机");
    if(!cycle.isSimulated()){outbox.enqueue("complete");sendOutboxHead();}
    showHome();
  }

  private void showSeal(){
    page("先停下，不必假装完成。",truthLine());
    label(cycle.completed()?"完成事实会保留。":"未完成也能封存；不会补写成完成。",16,Color.WHITE);
    EditText note=field("停在哪（可选一句）",cycle.text("stop_note").isEmpty()?cycle.text("stuck"):cycle.text("stop_note"));
    EditText recovery=field("明天第一步",cycle.recoveryCard());
    if(agent.configured())button("先保存停点，再让 Agent 提议",v->{cycle.seal(note.getText().toString(),recovery.getText().toString());liveStatus.setText("PHONE SAVED · 正在请求真实 LLM 候选");requestProposal(cycle.text("goal"),note.getText().toString(),12,null,null,recovery);});
    button("确认并封存",v->{
      cycle.seal(note.getText().toString(),recovery.getText().toString());
      if(!cycle.isSimulated()){outbox.enqueue("seal");sendOutboxHead();}
      toast("封存已保存；网络或硬件失败不会丢失这句话");showHome();
    });
    button("返回今日卡",v->showHome());
  }

  private void showResume(){
    page("昨天停在这里。",truthLine()+" · DEMO DAY "+cycle.day());
    label("STOP NOTE\n"+cycle.stopNote(),17,Color.WHITE);
    label("FIRST STEP\n"+cycle.recoveryCard(),19,lime);
    button("确认接回这一步",v->{cycle.resumeExisting();showHome();});
    button("编辑恢复动作",v->showNewAction());
  }

  private void showNewAction(){
    page("今天需要一张新卡。",truthLine());
    label("昨天已完成；同一动作不会自动再算一天。",16,Color.WHITE);
    EditText action=field("今天最小一步",""); EditText done=field("新的完成条件","");
    button("确认新动作",v->{if(action.length()==0||done.length()==0){toast("请确认动作与完成条件");return;}cycle.confirmNewAction(action.getText().toString(),done.getText().toString());showHome();});
  }

  private void showReview(){
    page("十日周期到这里。",truthLine());
    label("完成了什么\n"+(cycle.completed()?cycle.text("action"):"没有把未完成改写成完成"),16,Color.WHITE);
    label("留下的入口\n"+cycle.recoveryCard(),16,lime);
    label("P0 不会自动进入第 11 天。",14,Color.LTGRAY);
  }

  private void showSettings(){
    page("Agent 与设备设置","API Key 使用 Android Keystore 加密；不会写入 Git 或日志");
    EditText url=field("OpenAI-compatible HTTPS endpoint",prefs.getString("llm_url",""));
    EditText model=field("model",prefs.getString("llm_model",""));
    EditText key=field("API key（留空则保留已有）",""); key.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_PASSWORD);
    button("保存本机配置",v->{try{if(!key.getText().toString().isEmpty())agent.secrets().put(key.getText().toString());prefs.edit().putString("llm_url",url.getText().toString().trim()).putString("llm_model",model.getText().toString().trim()).remove("llm_key").commit();toast("设置已保存在本机；尚未代表线上调用成功");showHome();}catch(Exception error){liveStatus.setText("KEYSTORE ERROR · "+error.getClass().getSimpleName());}});
    button("返回",v->showHome());
  }

  private void requestProposal(String goal,String stuck,int minutes,EditText action,EditText done,EditText recovery){
    liveStatus.setText("REAL LLM REQUEST · 发送字段：目标、卡点、剩余分钟");
    new Thread(()->{try{AgentClient.Proposal proposal=agent.propose(goal,stuck,minutes);runOnUiThread(()->{if(action!=null)action.setText(proposal.action);if(done!=null)done.setText(proposal.doneWhen);if(recovery!=null)recovery.setText(proposal.recovery);liveStatus.setText("REAL LLM CANDIDATE · 必须由你确认\n"+proposal.explanation);});}catch(Exception error){runOnUiThread(()->liveStatus.setText("LLM FAILED · 已保留本地内容 · "+error.getMessage()));}},"tenfold-agent").start();
  }

  private void connectOrRetry(){
    cycle.chooseMode(CycleState.MODE_USB); cycle.markPending(cycle.commandId()); usb.requestOrConnect();
    showHome();
  }

  @Override public void onUsbState(String state){
    if(liveStatus!=null)liveStatus.setText(state+"\n"+truthLine());
  }
  @Override public void onUsbError(String code){if(liveStatus!=null)liveStatus.setText("USB ERROR · "+code+"\n手机事实仍保留");}
  @Override public void onFrame(JSONObject frame){
    String type=frame.optString("type");
    if("ack".equals(type)&&frame.optBoolean("persisted",false)){
      boolean accepted=frame.optInt("protocol",-1)==1&&cycle.acceptDeviceAck(frame.optString("command_id"),frame.optString("cycle_id"),frame.optInt("revision",-1));
      if(liveStatus!=null)liveStatus.setText(accepted?"USB DEVICE · matching persisted ACK":"USB DEVICE · stale/mismatched ACK ignored");
    }else if("event_ack".equals(type)&&frame.optBoolean("persisted",false)){
      int seq=frame.optInt("seq",-1);boolean matches=frame.optString("cycle_id").equals(cycle.text("cycle_id"))&&frame.optString("command_id").equals(cycle.commandId())&&frame.optInt("revision",-1)==prefs.getInt("revision",1);
      if(matches&&outbox.acknowledge(seq)){if(liveStatus!=null)liveStatus.setText("DEVICE EVENT SAVED · seq "+seq);sendOutboxHead();}
    }else if("event".equals(type)){
      int seq=frame.optInt("seq",-1);if(cycle.acceptDeviceEvent(seq,frame.optString("event_type")))usb.send(DeviceProtocol.eventAck(seq));showHome();
    }else if("hello".equals(type)){usb.send(DeviceProtocol.query(prefs));}
    else if("status".equals(type)){
      boolean matched=frame.optBoolean("persisted",false)&&cycle.acceptDeviceAck(frame.optString("command_id"),frame.optString("cycle_id"),frame.optInt("revision",-1));
      if(!matched)usb.send(DeviceProtocol.offer(prefs));else sendOutboxHead();showHome();
    }
  }
  private void sendOutboxHead(){JSONObject pending=outbox.peek();if(pending!=null)usb.send(pending);}
  private int clampMinutes(String raw){try{return Math.max(5,Math.min(45,Integer.parseInt(raw)));}catch(Exception ignored){return 12;}}
  private void toast(String message){Toast.makeText(this,message,Toast.LENGTH_LONG).show();}
}
