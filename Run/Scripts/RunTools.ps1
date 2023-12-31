
# 執行的輔助程式

$toolName, $otherArgs = $args

$ErrorActionPreference = "Stop"

# chcp 65001
# $OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
# $OutputEncoding


# 複製原始碼，選擇工具，呼叫

$PROJECT_ROOT_PATH = "$PSScriptRoot\..\.."
# $CODE_TOOL_PATH = 
# $WORK_PATH = 
$SCRIPT_PATH = "$PROJECT_ROOT_PATH\Run\Scripts"

switch ($toolName) {
    file2sql {
        # 更新原始碼
        # $todayDate = Get-Date
        # & $SCRIPT_PATH\Utility.ps1 UpdateSource test $todayDate

        # 暫時的，複製程式碼檔案
        $workPath = "$PROJECT_ROOT_PATH\Run\Lastest\test"
        $sourceDir = "$PROJECT_ROOT_PATH\Code\Tools"
        & $SCRIPT_PATH\Utility.ps1 RemoveFolder $workPath\Tools
        Copy-Item $sourceDir -Destination $workPath -Recurse

        # 執行
        Push-Location $workPath
        if ($args.Count -eq 2) {
            python -m Tools.FileToMysql $otherArgs
        } else {
            python -m Tools.FileToMysql @otherArgs
        }
        Pop-Location
    }


    Default { Write-Host "找不到工具" $toolName }
}
