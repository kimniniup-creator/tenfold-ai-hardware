param(
  [Parameter(Mandatory = $true)][string]$Port,
  [ValidateSet('Update', 'Provision', 'Factory')][string]$Mode = 'Update'
)

$ErrorActionPreference = 'Stop'
$releaseRoot = $PSScriptRoot
$esptool = Join-Path $env:USERPROFILE '.platformio\packages\tool-esptoolpy\esptool.py'
if (-not (Test-Path -LiteralPath $esptool)) {
  throw 'PlatformIO esptool is missing. Run: python -m platformio run -d firmware'
}

$common = @(
  $esptool, '--chip', 'esp32s3', '--port', $Port, '--baud', '460800',
  '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z',
  '--flash_mode', 'dio', '--flash_freq', '80m', '--flash_size', '8MB'
)

switch ($Mode) {
  'Update' {
    & python @common 0x10000 (Join-Path $releaseRoot 'firmware.bin')
  }
  'Provision' {
    & python @common 0x0000 (Join-Path $releaseRoot 'bootloader.bin') `
      0x8000 (Join-Path $releaseRoot 'partitions.bin') `
      0xe000 (Join-Path $releaseRoot 'boot_app0.bin') `
      0x10000 (Join-Path $releaseRoot 'firmware.bin')
  }
  'Factory' {
    Write-Warning 'Factory mode writes the merged image at 0x0 and overwrites the NVS gap. Existing Tenfold state will be lost.'
    & python @common 0x0000 (Join-Path $releaseRoot 'tenfold-p0-factory.bin')
  }
}

if ($LASTEXITCODE -ne 0) { throw "esptool failed with exit code $LASTEXITCODE" }
