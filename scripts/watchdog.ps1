$BotScript = "bot\bot.py"
$PythonPath = "python"

Write-Host "--- MONITOR DE INMORTALIDAD ACADEMIC-OS V5.0 ---" -ForegroundColor Cyan

while($true) {
    # Buscar el proceso específico del nuevo bot usando WMI para ser más compatible en Windows
    $process = Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like "*bot\bot.py*" }
    
    if ($null -eq $process) {
        Write-Host "[!] ALERTA: Agente caído. Resucitando..." -ForegroundColor Red
        Start-Process -FilePath $PythonPath -ArgumentList $BotScript -WindowStyle Hidden
        Write-Host "[+] Agente resucitado exitosamente." -ForegroundColor Green
    }
    
    Start-Sleep -Seconds 20
}
