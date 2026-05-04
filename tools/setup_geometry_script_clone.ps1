param(
    [string]$RepoUrl = "https://github.com/carson-katri/geometry-script.git",
    [string]$Branch = "vibegeometry/blender-5-nested-tree-groups"
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$target = Join-Path $root "external\geometry-script"
$patch = Join-Path $root "patches\geometry-script\0001-fix-nested-tree-group-references-on-blender-4.patch"

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

$alreadyApplied = git -C $target log --oneline --grep "Fix nested tree group references on Blender 4+" -1
if (!$alreadyApplied) {
    git -C $target am $patch
}

git -C $target status --short --branch
