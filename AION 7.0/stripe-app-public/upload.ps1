$env:Path = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\Stripe.StripeCLI_Microsoft.Winget.Source_8wekyb3d8bbwe;$env:Path"
Set-Location "C:\Users\crist\Projetos\A2A - Projato Econosystens 2.0\Ecosystem 2.0\stripe-app"
Write-Host "Y" | stripe apps upload
