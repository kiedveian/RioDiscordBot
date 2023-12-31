
# param(
#     $toolName, $paras
# )

$toolName, $otherArgs = $args


$ErrorActionPreference = "Stop"

$SOURCE_PATH = "D:\data\Git\RioTest\DiscordBot\"
$PROJECT_ROOT_PATH = "$PSScriptRoot\..\.."
$BACKUP_PATH = "$PROJECT_ROOT_PATH\Run\Backup"
$LASTEST_PATH = "$PROJECT_ROOT_PATH\Run\Lastest"

function Remove-Rio-Dir {
    param (
        $folderPath
    )
    If (Test-Path -Path $folderPath) {
        Remove-Item $folderPath -Recurse
    }
    else {
        Write-Host "刪除資料夾不存在 $folderPath "
        <# Action when all if and elseif conditions are false #>
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


function Update-Rio-Source {
    param (
        $branch, $time
    )

    Write-Host $branch
    Write-Host $time

    $timeDirName = $time.ToString("yyyy-MMdd_hhmmss")
    $backupPath = "$BACKUP_PATH\$branch\$timeDirName"
    $workPath = "$LASTEST_PATH\$branch"
    Remove-Rio-Dir $workPath -Recurse
    New-Rio-Folder $workPath
    New-Rio-Folder $backupPath

    $folderList = "BotComponent", "BotMain", "Utility"
    $fileList = "DiscordBotEnter.py", ".env"
    foreach ($folder in $folderList) {
        Copy-Item "$SOURCE_PATH\$folder\" -Destination "$workPath\$folder\" -Recurse
    }
    foreach ($filename in $fileList) {
        Copy-Item "$SOURCE_PATH\$filename" -Destination "$workPath\$filename"
    }
    Copy-Item "$workPath\*" -Destination $backupPath
}


# $argString = [string]$paras
# $argString = $paras -join ' '
# Write-Host 參數 $argString
# Write-Host $otherArgs

switch ($toolName) {
    RemoveFolder { 
        if ($args.Count -eq 2) {
            Remove-Rio-Dir $otherArgs
        }
        else {
            Remove-Rio-Dir @otherArgs
        }
        
    }
    NewFolder {
        New-Rio-Folder @otherArgs
    }
    UpdateSource {
        Update-Rio-Source @otherArgs
    }
    Default { Write-Output 找不到指令 }
}