package io.tenfold.app;

import android.content.SharedPreferences;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import org.json.JSONArray;
import org.json.JSONObject;

/** OpenAI-compatible client. Call on a worker thread; returned text is always an unconfirmed candidate. */
final class AgentClient {
  static final class Proposal {
    final String action, doneWhen, recovery, explanation;
    Proposal(String action,String doneWhen,String recovery,String explanation){this.action=action;this.doneWhen=doneWhen;this.recovery=recovery;this.explanation=explanation;}
  }
  private final SharedPreferences prefs; private final SecretStore secrets;
  AgentClient(SharedPreferences prefs){this.prefs=prefs;this.secrets=new SecretStore(prefs);}
  boolean configured(){return !prefs.getString("llm_url","").isEmpty()&&!prefs.getString("llm_model","").isEmpty()&&!prefs.getString("llm_key_cipher","").isEmpty();}
  Proposal propose(String goal,String stuck,int minutes) throws Exception {
    if(!configured())throw new IllegalStateException("LLM_NOT_CONFIGURED");
    URL url=new URL(prefs.getString("llm_url","")); if(!"https".equalsIgnoreCase(url.getProtocol()))throw new IllegalArgumentException("HTTPS_REQUIRED");
    JSONObject schema=new JSONObject().put("name","tenfold_proposal").put("strict",true).put("schema",new JSONObject()
      .put("type","object").put("additionalProperties",false).put("required",new JSONArray().put("action").put("done_when").put("recovery").put("explanation"))
      .put("properties",new JSONObject().put("action",stringSchema()).put("done_when",stringSchema()).put("recovery",stringSchema()).put("explanation",stringSchema())));
    String prompt="Goal: "+goal+"\nCurrent stopping point: "+stuck+"\nMinutes: "+minutes+". Propose only a sufficient stopping boundary and tomorrow's first step; do not add projects.";
    JSONObject request=new JSONObject().put("model",prefs.getString("llm_model","")).put("temperature",0.2)
      .put("messages",new JSONArray().put(new JSONObject().put("role","system").put("content","You are Tenfold. Reduce scope. Return strict JSON only."))
      .put(new JSONObject().put("role","user").put("content",prompt)))
      .put("response_format",new JSONObject().put("type","json_schema").put("json_schema",schema));
    HttpURLConnection c=(HttpURLConnection)url.openConnection();
    try {
      c.setConnectTimeout(8000);c.setReadTimeout(15000);c.setRequestMethod("POST");c.setDoOutput(true);
      c.setRequestProperty("Authorization","Bearer "+secrets.get());c.setRequestProperty("Content-Type","application/json");
      c.getOutputStream().write(request.toString().getBytes(StandardCharsets.UTF_8));
      int code=c.getResponseCode();if(code<200||code>=300)throw new IllegalStateException("LLM_HTTP_"+code);
      StringBuilder body=new StringBuilder();
      try(BufferedReader reader=new BufferedReader(new InputStreamReader(c.getInputStream(),StandardCharsets.UTF_8))){String line;while((line=reader.readLine())!=null){body.append(line);if(body.length()>65536)throw new IllegalStateException("LLM_RESPONSE_TOO_LARGE");}}
      JSONObject root=new JSONObject(body.toString());String content=root.getJSONArray("choices").getJSONObject(0).getJSONObject("message").getString("content");
      JSONObject value=new JSONObject(content);String action=required(value,"action",160),done=required(value,"done_when",160),recovery=required(value,"recovery",160),why=required(value,"explanation",240);
      return new Proposal(action,done,recovery,why);
    } finally { c.disconnect(); }
  }
  private static JSONObject stringSchema() throws Exception {return new JSONObject().put("type","string").put("minLength",1).put("maxLength",240);}
  private static String required(JSONObject value,String key,int max) throws Exception {String text=value.getString(key).trim();if(text.isEmpty()||text.length()>max)throw new IllegalArgumentException("INVALID_"+key);return text;}
  SecretStore secrets(){return secrets;}
}
