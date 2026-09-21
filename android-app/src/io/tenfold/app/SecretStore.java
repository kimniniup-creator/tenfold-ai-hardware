package io.tenfold.app;

import android.content.SharedPreferences;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

final class SecretStore {
  private static final String ALIAS="tenfold.llm.key";
  private final SharedPreferences prefs;
  SecretStore(SharedPreferences prefs){this.prefs=prefs;}
  void put(String value) throws Exception {
    SecretKey key=getOrCreate(); Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(Cipher.ENCRYPT_MODE,key); byte[] encrypted=cipher.doFinal(value.getBytes(StandardCharsets.UTF_8));
    prefs.edit().putString("llm_key_cipher",Base64.encodeToString(encrypted,Base64.NO_WRAP))
      .putString("llm_key_iv",Base64.encodeToString(cipher.getIV(),Base64.NO_WRAP)).apply();
  }
  String get() throws Exception {
    String ciphertext=prefs.getString("llm_key_cipher",""); String iv=prefs.getString("llm_key_iv","");
    if(ciphertext.isEmpty()||iv.isEmpty())return ""; Cipher cipher=Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(Cipher.DECRYPT_MODE,getOrCreate(),new GCMParameterSpec(128,Base64.decode(iv,Base64.NO_WRAP)));
    return new String(cipher.doFinal(Base64.decode(ciphertext,Base64.NO_WRAP)),StandardCharsets.UTF_8);
  }
  private SecretKey getOrCreate() throws Exception {
    KeyStore store=KeyStore.getInstance("AndroidKeyStore");store.load(null);
    if(store.containsAlias(ALIAS))return (SecretKey)store.getKey(ALIAS,null);
    KeyGenerator generator=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");
    generator.init(new KeyGenParameterSpec.Builder(ALIAS,KeyProperties.PURPOSE_ENCRYPT|KeyProperties.PURPOSE_DECRYPT)
      .setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());
    return generator.generateKey();
  }
}
