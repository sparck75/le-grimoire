# Recipe Backup & Restore - PowerShell Wrapper
# Makes it easier to run backup/restore commands on Windows

param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet('import', 'export', 'backup', 'restore', 'list')]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$FilePath,
    
    [switch]$Clear
)

function Get-DockerFilePath {
    param([string]$LocalPath)
    
    # If path is already absolute, use as-is
    if ($LocalPath -match '^[A-Za-z]:') {
        # Convert Windows path to relative if in project
        $projectRoot = "d:\Github\le-grimoire"
        if ($LocalPath.StartsWith($projectRoot)) {
            $relativePath = $LocalPath.Substring($projectRoot.Length).TrimStart('\')
            return "/app/$($relativePath.Replace('\', '/'))"
        }
    }
    
    # If relative path, assume it's in backend directory
    if (-not $LocalPath.StartsWith('/')) {
        return "/app/$FilePath"
    }
    
    return $LocalPath
}

# Build the docker command
$dockerCmd = "docker-compose exec backend python scripts/backup_restore_recipes.py $Command"

switch ($Command) {
    'import' {
        if (-not $FilePath) {
            Write-Host "Error: Please provide a file path to import" -ForegroundColor Red
            Write-Host "Usage: .\backup-recipes.ps1 import file.json" -ForegroundColor Yellow
            exit 1
        }
        
        # Check if file exists locally
        if (Test-Path $FilePath) {
            # Copy to backend directory if not already there
            $backendPath = "backend\$(Split-Path -Leaf $FilePath)"
            if (-not (Test-Path $backendPath)) {
                Write-Host "Copying file to backend directory..." -ForegroundColor Cyan
                Copy-Item $FilePath $backendPath
            }
            $dockerPath = "/app/$(Split-Path -Leaf $FilePath)"
        } else {
            $dockerPath = Get-DockerFilePath $FilePath
        }
        
        $dockerCmd += " $dockerPath"
    }
    
    'export' {
        if (-not $FilePath) {
            Write-Host "Error: Please provide output file path" -ForegroundColor Red
            Write-Host "Usage: .\backup-recipes.ps1 export output.json" -ForegroundColor Yellow
            exit 1
        }
        
        $dockerPath = Get-DockerFilePath $FilePath
        $dockerCmd += " $dockerPath"
    }
    
    'restore' {
        if (-not $FilePath) {
            Write-Host "Error: Please provide backup file path" -ForegroundColor Red
            Write-Host "Usage: .\backup-recipes.ps1 restore backup.json [-Clear]" -ForegroundColor Yellow
            exit 1
        }
        
        $dockerPath = Get-DockerFilePath $FilePath
        $dockerCmd += " $dockerPath"
        
        if ($Clear) {
            $dockerCmd += " --clear"
        }
    }
    
    'backup' {
        # No additional parameters needed
    }
    
    'list' {
        # No additional parameters needed
    }
}

# Display command being run
Write-Host "Running: $dockerCmd" -ForegroundColor Blue
Write-Host ""

# Execute the command
Invoke-Expression $dockerCmd

# If export or backup, show where file was created
if ($Command -eq 'export' -or $Command -eq 'backup') {
    Write-Host ""
    Write-Host "Tip: Backup files are in the container at /backups/" -ForegroundColor Green
    Write-Host "   To access them, use: docker-compose cp backend:/backups/ ./backups/" -ForegroundColor Gray
}
