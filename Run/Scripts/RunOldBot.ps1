$ErrorActionPreference = "Stop"

$SOURCE_PATH = "D:\data\Git\RioTest\DiscordBot\"
$PROJECT_ROOT_PATH = "$PSScriptRoot\..\.."
# $SOURCE_PATH = "$PROJECT_ROOT_PATH\Code\"
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
    # $msg = New-Rio-Folder $workPath
    # $msg = New-Rio-Folder $backupPath

    $folderList = "BotComponent", "BotMain", "Utility"
    $fileList = "DiscordBotEnter.py", ".env"
    # $folderList = "Bot", "Utility"
    # $fileList = "BotMain.py", ".env"
    foreach ($folder in $folderList) {
        Copy-Item "$SOURCE_PATH\$folder\" -Destination "$workPath\$folder\" -Recurse
    }
    foreach ($filename in $fileList) {
        Copy-Item "$SOURCE_PATH\$filename" -Destination "$workPath\$filename"
    }
    Copy-Item "$workPath\" -Destination "$backupPath\" -Recurse

    # New-Item -Path $lastestPath -Name $dirName -ItemType Directory
    # $todayDate = Get-Date
    # $tempDate = $todayDate.ToString("yyyy-MM-dd")
    # $str = $date.ToString("dd-MM-yyyy hh:mm:ss")
    # $tempDate1 = "{0:yyyy/MM/dd}" -f $todayDate

    # Push-Location D:\data\Git\Discord\Bot\Code\

    # Pop-Location
}

# 執行程式
# Get-Service -Name w32time

$branch = "test"
$sql = "test"

$currentTime = Get-Date
Copy-Rio-Source test $currentTime
# $specificDate = [datetime]"2023-04-02"

# Get-Location
Push-Location "$PSScriptRoot\..\Lastest\$branch"
# Get-Location

# $PSCommandPath

try {
    python .\DiscordBotEnter.py $branch $sql
    # python .\BotMain.py $branch $sql
}
finally {
    Pop-Location
}
