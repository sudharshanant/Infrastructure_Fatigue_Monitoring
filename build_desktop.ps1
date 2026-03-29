$ErrorActionPreference = "Stop"

$pythonExe = ".venv/Scripts/python.exe"
$appName = "InfrastructureFatigueApp"
$iconPath = "assets/app.ico"

if (-not (Test-Path $pythonExe)) {
    throw "Python environment not found at $pythonExe"
}

Write-Host "Installing desktop dependencies..."
& $pythonExe -m pip install -r requirements-desktop.txt

$pyInstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name", $appName,
    "--add-data", "templates;templates",
    "--add-data", "static;static",
    "--add-data", "data;data",
    "desktop_app.py"
)

if (Test-Path $iconPath) {
    Write-Host "Using icon: $iconPath"
    $pyInstallerArgs = @(
        "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", $appName,
        "--icon", $iconPath,
        "--add-data", "templates;templates",
        "--add-data", "static;static",
        "--add-data", "data;data",
        "desktop_app.py"
    )
} else {
    Write-Host "No icon found at $iconPath (continuing without custom icon)."
}

Write-Host "Building executable..."
& $pythonExe @pyInstallerArgs

Write-Host "Build complete: dist/$appName.exe"
Write-Host "Tip: To create installer, open installer/InfrastructureFatigueApp.iss in Inno Setup and compile."
