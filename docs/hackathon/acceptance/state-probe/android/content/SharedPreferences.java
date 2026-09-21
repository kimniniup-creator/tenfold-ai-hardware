package android.content;
public interface SharedPreferences {
  java.util.Map<String,?> getAll();
  String getString(String key,String fallback);
  int getInt(String key,int fallback);
  boolean getBoolean(String key,boolean fallback);
  Editor edit();
  interface Editor {
    Editor clear();
    Editor putLong(String key,long value);
    Editor putFloat(String key,float value);
    Editor remove(String key);
    Editor putString(String key,String value);
    Editor putInt(String key,int value);
    Editor putBoolean(String key,boolean value);
    boolean commit();
  }
}
