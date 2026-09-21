package io.tenfold.app;

import android.content.SharedPreferences;
import java.time.LocalDate;

/** Durable app facts. Device facts are never inferred from a successful USB write. */
final class CycleState {
  static final String MODE_SIMULATED = "SIMULATED";
  static final String MODE_USB = "USB_PENDING_ACK";
  private final SharedPreferences p;
  CycleState(SharedPreferences p) { this.p = p; }
  String mode() { return p.getString("mode", MODE_SIMULATED); }
  boolean isSimulated() { return MODE_SIMULATED.equals(mode()); }
  int demoDay() { return p.getInt("demo_day", 1); }
  boolean completed() { return p.getBoolean("completed", false); }
  String stopNote() { return p.getString("stop_note", ""); }
  String recoveryCard() { return p.getString("recovery_card", p.getString("action", "")); }
  void setMode(String value) { p.edit().putString("mode", value).apply(); }
  void seal(String note) { p.edit().putString("phase", "SEALED").putString("stop_note", note).putString("recovery_card", note.isEmpty() ? p.getString("action", "") : note).apply(); }
  void advanceDemoDay() {
    int next = demoDay() + 1;
    p.edit().putInt("demo_day", next).putBoolean("completed", false)
      .putString("phase", completed() ? "AWAITING_NEXT_ACTION" : "RESUME_AVAILABLE").apply();
  }
  boolean canComplete() { return !completed() && !"SEALED".equals(p.getString("phase", "")); }
}
