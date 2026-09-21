$ErrorActionPreference = 'Stop'
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
Push-Location $repoRoot
$sdk = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { 'E:\Android\Sdk' }
$bt = Join-Path $sdk 'build-tools\35.0.0'; $platform = Join-Path $sdk 'platforms\android-35\android.jar'
$out = [System.IO.Path]::GetFullPath((Join-Path $repoRoot 'android-app\out-release'))
$expectedOut = [System.IO.Path]::GetFullPath((Join-Path $repoRoot 'android-app\out-release'))
if ($out -ne $expectedOut -or -not $out.StartsWith($repoRoot + [System.IO.Path]::DirectorySeparatorChar)) { throw 'Unsafe output path' }
if (Test-Path -LiteralPath $out) { Remove-Item -LiteralPath $out -Recurse -Force }
New-Item -ItemType Directory -Force $out,"$out\classes","$out\dex" | Out-Null
& "$bt\aapt2.exe" compile --dir android-app\res -o "$out\res.zip"
if ($LASTEXITCODE -ne 0) { throw 'aapt2 compile failed' }
& "$bt\aapt2.exe" link --auto-add-overlay -o "$out\unsigned.apk" -I $platform --manifest android-app\AndroidManifest.xml -R "$out\res.zip"
if ($LASTEXITCODE -ne 0) { throw 'aapt2 link failed' }
$sources = Get-ChildItem android-app\src -Recurse -Filter *.java | ForEach-Object FullName
& javac -encoding UTF-8 -source 8 -target 8 -classpath $platform -d "$out\classes" $sources
if ($LASTEXITCODE -ne 0) { throw 'javac failed' }
& jar cf "$out\classes.jar" -C "$out\classes" .; if ($LASTEXITCODE -ne 0) { throw 'jar failed' }
& "$bt\d8.bat" --lib $platform --output "$out\dex" "$out\classes.jar"; if ($LASTEXITCODE -ne 0) { throw 'd8 failed' }
Copy-Item "$out\unsigned.apk" "$out\unaligned.apk"
Push-Location "$out\dex"; & "$bt\aapt.exe" add "..\unaligned.apk" classes.dex; Pop-Location
if ($LASTEXITCODE -ne 0) { throw 'aapt add dex failed' }
& "$bt\zipalign.exe" -f 4 "$out\unaligned.apk" "$out\tenfold-p0-unsigned.apk"
if ($LASTEXITCODE -ne 0) { throw 'zipalign failed' }
$signingDir = Join-Path $repoRoot '.signing'; New-Item -ItemType Directory -Force $signingDir | Out-Null
$key = "$signingDir\tenfold-demo.jks"; if (!(Test-Path $key)) { & keytool -genkeypair -keystore $key -storepass android -keypass android -alias tenfold -keyalg RSA -keysize 2048 -validity 3650 -dname 'CN=Tenfold P0, OU=Demo, O=Tenfold, C=CN' -noprompt }
& "$bt\apksigner.bat" sign --ks $key --ks-pass pass:android --key-pass pass:android --ks-key-alias tenfold --out "$out\tenfold-p0.apk" "$out\tenfold-p0-unsigned.apk"
if ($LASTEXITCODE -ne 0) { throw 'apksigner sign failed' }
& "$bt\apksigner.bat" verify --verbose "$out\tenfold-p0.apk"
if ($LASTEXITCODE -ne 0) { throw 'apksigner verify failed' }
if (-not ((& "$bt\aapt.exe" list "$out\tenfold-p0.apk") -contains 'classes.dex')) { throw 'APK is missing root classes.dex' }
Get-FileHash "$out\tenfold-p0.apk" -Algorithm SHA256
Pop-Location
