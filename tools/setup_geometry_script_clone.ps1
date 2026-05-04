param(
    [string]$RepoUrl = "https://github.com/carson-katri/geometry-script.git",
    [string]$Branch = "vibegeometry/blender-5-nodes-to-script"
)

$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$target = Join-Path $root "external\geometry-script"
$patchDir = Join-Path $root "patches\geometry-script"

function Test-GitPatch {
    param(
        [string]$Mode,
        [string]$PatchPath
    )

    $previous = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        if ($Mode -eq "Reverse") {
            & git -C $target apply --reverse --check $PatchPath 2>$null
        } else {
            & git -C $target apply --check $PatchPath 2>$null
        }
        return $LASTEXITCODE -eq 0
    } finally {
        $ErrorActionPreference = $previous
    }
}

if (!(Test-Path $target)) {
    New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
    git clone $RepoUrl $target
}

git -C $target fetch origin

$branches = git -C $target branch --list $Branch
if ($branches) {
    git -C $target switch $Branch
} else {
    git -C $target switch -c $Branch origin/main
}

$patches = Get-ChildItem -Path $patchDir -Filter "*.patch" | Sort-Object Name
foreach ($patch in $patches) {
    if (Test-GitPatch -Mode "Forward" -PatchPath $patch.FullName) {
        git -C $target am $patch.FullName
        continue
    }

    if (!(Test-GitPatch -Mode "Reverse" -PatchPath $patch.FullName)) {
        throw "Patch is neither applicable nor already applied: $($patch.FullName)"
    }
}

git -C $target status --short --branch
