$branch, $sql = $args

$ErrorActionPreference = "Stop"

$PROJECT_ROOT_PATH = "$PSScriptRoot\..\.."
$SOURCE_PATH = "$PROJECT_ROOT_PATH\Code\"
$BACKUP_PATH = "$PROJECT_ROOT_PATH\Run\Backup"
$LASTEST_PATH = "$PROJECT_ROOT_PATH\Run\Lastest"

# 工具函式

function Remove-Rio-Item {
    param (
        $folderPath
    )
    If (Test-Path -Path $folderPath) {
        Remove-Item $folderPath -Recurse
    }
    
}

function New-Rio-Folder {
    param (
        $folderPath
    )
    If (!(Test-Path -Path $folderPath)) {
        New-Item -ItemType Directory -Path $folderPath
    }
}


# 複製程式

function Copy-Rio-Source {
    param (
        $branch, $time
    )

    Write-Debug $branch
    Write-Debug $time

    $timeDirName = $time.ToString("yyyy-MMdd_HHmmss")
    $backupPath = "$BACKUP_PATH\$branch\$timeDirName"
    $workPath = "$LASTEST_PATH\$branch"
    Remove-Rio-Item $workPath -Recurse

    $folderList = "Bot", "Utility"
    $fileList = "BotMain.py", ".env"
    foreach ($folder in $folderList) {
        Copy-Item "$SOURCE_PATH\$folder\" -Destination "$workPath\$folder\" -Recurse
    }
    foreach ($filename in $fileList) {
        Copy-Item "$SOURCE_PATH\$filename" -Destination "$workPath\$filename"
    }
    # 複製到備份區
    Copy-Item "$workPath\" -Destination "$backupPath\" -Recurse
}

$currentTime = Get-Date
Copy-Rio-Source $branch $currentTime

# Get-Location
Push-Location "$PSScriptRoot\..\Lastest\$branch"
# Get-Location


try {
    python .\BotMain.py $branch $sql
}
finally {
    Pop-Location
}

