$ErrorActionPreference = "Stop"
$stripe = "C:\Users\crist\AppData\Local\Microsoft\WinGet\Packages\Stripe.StripeCLI_Microsoft.Winget.Source_8wekyb3d8bbwe\stripe.exe"
$appDir = "C:\Users\crist\Projetos\A2A - Projato Econosystens 2.0\Ecosystem 2.0\stripe-app"

Set-Location $appDir

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $stripe
$psi.Arguments = "apps upload"
$psi.UseShellExecute = $false
$psi.RedirectStandardInput = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.WorkingDirectory = $appDir

$p = New-Object System.Diagnostics.Process
$p.StartInfo = $psi
$p.Start() | Out-Null

Start-Sleep -Milliseconds 2000
$p.StandardInput.WriteLine("Y")
$p.StandardInput.Close()

$output = $p.StandardOutput.ReadToEnd()
$errorOutput = $p.StandardError.ReadToEnd()
$p.WaitForExit(30000)

Write-Output "Exit code: $($p.ExitCode)"
Write-Output $output
if ($errorOutput) { Write-Output "STDERR: $errorOutput" }
