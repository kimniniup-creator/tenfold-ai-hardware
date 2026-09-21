param([string]$Revision='0daf340988157b66cca29403c9e7492975b4533f',[string]$Probe='StateProbe')
$ErrorActionPreference='Stop'
$scratch=Join-Path $PSScriptRoot 'runtime'
New-Item -ItemType Directory -Force -Path $scratch | Out-Null
$source=git show "${Revision}:android-app/src/io/tenfold/app/CycleState.java"
if($LASTEXITCODE -ne 0){throw 'Cannot load fixed production revision'}
$source | Set-Content -LiteralPath (Join-Path $scratch 'CycleState.java') -Encoding utf8
& javac -encoding UTF-8 -d $scratch (Join-Path $PSScriptRoot 'android/content/SharedPreferences.java') (Join-Path $scratch 'CycleState.java') (Join-Path $PSScriptRoot "io/tenfold/app/$Probe.java")
if($LASTEXITCODE -ne 0){throw 'Probe compilation failed'}
"SOURCE_REVISION=$Revision"
& java -cp $scratch "io.tenfold.app.$Probe"
if($LASTEXITCODE -ne 0){throw 'Probe execution failed'}
