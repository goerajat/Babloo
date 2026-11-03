# Fetch every file needed to set up Babloo (Windows). Safe to re-run; existing files are skipped.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force -Path files | Out-Null
Set-Location files

function Fetch($url, $out) {
  if (Test-Path $out) { Write-Host "  already have $out"; return }
  Write-Host "  downloading $out"
  Invoke-WebRequest -Uri $url -OutFile "$out.part" -UseBasicParsing
  Move-Item "$out.part" $out
}
function GhLatestAsset($repo, $pattern) {
  $rel = Invoke-RestMethod "https://api.github.com/repos/$repo/releases/latest"
  ($rel.assets | Where-Object { $_.name -match $pattern } | Select-Object -First 1).browser_download_url
}

Write-Host "== Raspberry Pi Imager"
Fetch "https://downloads.raspberrypi.org/imager/imager_latest.exe" "imager_latest.exe"

Write-Host "== Raspberry Pi OS Lite (64-bit)"
Fetch "https://downloads.raspberrypi.com/raspios_lite_arm64_latest" "raspios_lite_arm64_latest.img.xz"
try {
  Fetch "https://downloads.raspberrypi.com/raspios_lite_arm64_latest.sha256" "raspios_lite_arm64_latest.img.xz.sha256"
  $want = (Get-Content raspios_lite_arm64_latest.img.xz.sha256).Split(" ")[0]
  $have = (Get-FileHash raspios_lite_arm64_latest.img.xz -Algorithm SHA256).Hash.ToLower()
  if ($want -eq $have) { Write-Host "  checksum OK" } else { throw "CHECKSUM MISMATCH: delete the file and re-run" }
} catch { Write-Host "  (checksum not verified: $_)" }

Write-Host "== ev3dev (EV3 image)"
try {
  Fetch "https://github.com/ev3dev/ev3dev/releases/download/ev3dev-stretch-2020-04-10/ev3dev-stretch-ev3-generic-2020-04-10.zip" "ev3dev-stretch-ev3-generic-2020-04-10.zip"
} catch {
  Write-Host "  pinned URL failed, asking GitHub for the latest EV3 image"
  $u = GhLatestAsset "ev3dev/ev3dev" 'ev3-generic.*\.(zip|img\.xz)$'
  Fetch $u (Split-Path $u -Leaf)
}
# The zip nests the .img inside a folder with metadata; Imager needs the bare .img.
if (-not (Test-Path "ev3dev-stretch-ev3-generic-2020-04-10.img")) {
  Write-Host "  extracting .img (Imager cannot use the nested zip)"
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $z = [IO.Compression.ZipFile]::OpenRead((Resolve-Path "ev3dev-stretch-ev3-generic-2020-04-10.zip"))
  $e = $z.Entries | Where-Object { $_.Name -like "*.img" } | Select-Object -First 1
  [IO.Compression.ZipFileExtensions]::ExtractToFile($e, (Join-Path (Get-Location) $e.Name), $true)
  $z.Dispose()
}

Write-Host "== MediaMTX (linux arm64, for the Pi)"
$u = GhLatestAsset "bluenviron/mediamtx" 'linux_arm64(v8)?\.tar\.gz$'
Fetch $u (Split-Path $u -Leaf)

Write-Host "== balenaEtcher (optional)"
try {
  $u = GhLatestAsset "balena-io/etcher" 'Setup.*\.exe$'
  Fetch $u (Split-Path $u -Leaf)
} catch { Write-Host "  skipped (could not resolve asset)" }

Write-Host ""
Write-Host "== Checksums"
Get-ChildItem -File | Where-Object { $_.Name -notmatch '\.sha256$' } | ForEach-Object {
  "{0}  {1}" -f (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower(), $_.Name
}
Write-Host ""
Write-Host "Done. Files are in $(Get-Location)"
