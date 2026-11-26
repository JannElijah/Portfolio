<#
.SYNOPSIS
    WinOps standalone PowerShell workstation baseline audit script.
.DESCRIPTION
    Collects host model, BIOS serial number, OS build, physical RAM, disk capacity,
    and Windows Firewall profile status into JSON for IT asset onboarding.
#>
[CmdletBinding()]
param(
    [string]$OutFile = "workstation_audit.json"
)

$ErrorActionPreference = 'Stop'

$cs = Get-CimInstance Win32_ComputerSystem
$bios = Get-CimInstance Win32_BIOS
$os = Get-CimInstance Win32_OperatingSystem
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$fw = @(Get-NetFirewallProfile | Select-Object Name, Enabled)

$report = [ordered]@{
    audited_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    hostname       = $env:COMPUTERNAME
    manufacturer   = $cs.Manufacturer
    model          = $cs.Model
    serial_number  = $bios.SerialNumber
    os_caption     = $os.Caption
    os_build       = $os.BuildNumber
    ram_gb         = [math]::Round($cs.TotalPhysicalMemory / 1GB, 2)
    c_free_gb      = [math]::Round($disk.FreeSpace / 1GB, 2)
    firewall       = $fw
}

$report | ConvertTo-Json -Depth 4 | Set-Content -Path $OutFile -Encoding UTF8
Write-Output "Saved workstation audit to $OutFile"
