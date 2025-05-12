function djrun {
    Set-Location -Path "C:\Users\AbdihakimYusufHassan\billing-audit-system"
    Get-Content .env.local | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]*)\s*=\s*(.*)\s*$") {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
    python manage.py runserver
}

