$ErrorActionPreference = 'Stop'
$sdk = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { 'E:\Android\Sdk' }
$bt = Join-Path $sdk 'build-tools\35.0.0'; $platform = Join-Path $sdk 'platforms\android-35\android.jar'
$out = 'android-app\out-release'; New-Item -ItemType Directory -Force $out,"$out\classes","$out\dex" | Out-Null
& "$bt\aapt2.exe" compile --dir android-app\res -o "$out\res.zip"
& "$bt\aapt2.exe" link --auto-add-overlay -o "$out\unsigned.apk" -I $platform --manifest android-app\AndroidManifest.xml -R "$out\res.zip"
$sources = Get-ChildItem android-app\src -Recurse -Filter *.java | ForEach-Object FullName
& javac -encoding UTF-8 -source 8 -target 8 -classpath $platform -d "$out\classes" $sources
& jar cf "$out\classes.jar" -C "$out\classes" .; & "$bt\d8.bat" --lib $platform --output "$out\dex" "$out\classes.jar"
Copy-Item "$out\unsigned.apk" "$out\unaligned.apk"; & "$bt\aapt.exe" add "$out\unaligned.apk" "$out\dex\classes.dex"; & "$bt\zipalign.exe" -f 4 "$out\unaligned.apk" "$out\tenfold-p0-unsigned.apk"
$key = "$out\debug-keystore.jks"; if (!(Test-Path $key)) { & keytool -genkeypair -keystore $key -storepass android -keypass android -alias tenfold -keyalg RSA -keysize 2048 -validity 3650 -dname 'CN=Tenfold P0, OU=Demo, O=Tenfold, C=CN' -noprompt }
& "$bt\apksigner.bat" sign --ks $key --ks-pass pass:android --key-pass pass:android --ks-key-alias tenfold --out "$out\tenfold-p0.apk" "$out\tenfold-p0-unsigned.apk"
& "$bt\apksigner.bat" verify --verbose "$out\tenfold-p0.apk"; Get-FileHash "$out\tenfold-p0.apk" -Algorithm SHA256
