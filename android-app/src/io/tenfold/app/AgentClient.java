package io.tenfold.app;

import android.content.SharedPreferences;
import java.net.HttpURLConnection; import java.net.URL; import java.nio.charset.StandardCharsets;

/** Optional OpenAI-compatible call. It is disabled until the user saves a URL, model and key locally. */
final class AgentClient {
  private final SharedPreferences p;
  AgentClient(SharedPreferences p) { this.p = p; }
  boolean configured() { return !p.getString("llm_url", "").isEmpty() && !p.getString("llm_key", "").isEmpty(); }
  String propose(String userJson) throws Exception {
    if (!configured()) throw new IllegalStateException("LLM_NOT_CONFIGURED");
    HttpURLConnection c=(HttpURLConnection)new URL(p.getString("llm_url", "")).openConnection();
    c.setConnectTimeout(8000); c.setReadTimeout(15000); c.setRequestMethod("POST"); c.setDoOutput(true);
    c.setRequestProperty("Authorization", "Bearer " + p.getString("llm_key", ""));
    c.setRequestProperty("Content-Type", "application/json");
    c.getOutputStream().write(userJson.getBytes(StandardCharsets.UTF_8));
    if (c.getResponseCode() < 200 || c.getResponseCode() >= 300) throw new IllegalStateException("LLM_HTTP_" + c.getResponseCode());
    return "candidate received; user confirmation required"; // schema parsing is deliberately not faked.
  }
}
