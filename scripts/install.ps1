# Windows installer for Claude Code and opencode. Idempotent; same steps as install.sh.
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $PSScriptRoot
$src  = Join-Path $here 'skills\twice-exceptional-skill\SKILL.md'
$cl   = Join-Path $HOME '.claude'
$oc   = Join-Path $HOME '.config\opencode'
$imp  = '@~/.claude/skills/twice-exceptional-skill/SKILL.md'
$ins  = '~/.claude/skills/twice-exceptional-skill/SKILL.md'

# UTF-8 without BOM, on both Windows PowerShell 5.1 and PowerShell 7
function Write-Utf8($path, $text) { [IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding $false)) }

foreach ($root in @($cl, $oc)) {
    $dir = Join-Path $root 'skills\twice-exceptional-skill'
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Copy-Item -Force $src (Join-Path $dir 'SKILL.md')
}

$claudeMd = Join-Path $cl 'CLAUDE.md'
if (-not (Test-Path $claudeMd)) { New-Item -ItemType File -Path $claudeMd | Out-Null }
$lines = @(Get-Content $claudeMd)
if ($lines -notcontains $imp) { Add-Content -Path $claudeMd -Value $imp }

$ocJson = Join-Path $oc 'opencode.json'
if (Test-Path $ocJson) {
    $stamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    Copy-Item $ocJson "$ocJson.bak.$stamp"
    $cfg = Get-Content -Raw $ocJson | ConvertFrom-Json
    if (-not ($cfg.PSObject.Properties.Name -contains 'instructions')) {
        $cfg | Add-Member -NotePropertyName instructions -NotePropertyValue @()
    }
    if (@($cfg.instructions) -notcontains $ins) {
        $cfg.instructions = @($cfg.instructions) + $ins
    }
    Write-Utf8 $ocJson ($cfg | ConvertTo-Json -Depth 32)
} else {
    $cfg = [ordered]@{ '$schema' = 'https://opencode.ai/config.json'; instructions = @($ins) }
    Write-Utf8 $ocJson ($cfg | ConvertTo-Json -Depth 4)
}
Write-Host 'twice-exceptional-skill installed (Claude Code + opencode).'
