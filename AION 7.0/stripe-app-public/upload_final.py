import subprocess, sys, os, time

stripe = r"C:\Users\crist\AppData\Local\Microsoft\WinGet\Packages\Stripe.StripeCLI_Microsoft.Winget.Source_8wekyb3d8bbwe\stripe.exe"
app_dir = r"C:\Users\crist\Projetos\A2A - Projato Econosystens 2.0\Ecosystem 2.0\stripe-app"

os.chdir(app_dir)
proc = subprocess.Popen(
    [stripe, "apps", "upload"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd=app_dir,
)
time.sleep(3)
proc.stdin.write(b"Y\n")
proc.stdin.flush()
proc.stdin.close()
stdout, stderr = proc.communicate(timeout=30)
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
text = stdout.decode("utf-8", errors="replace")
print(text)
if stderr:
    print("STDERR:", stderr.decode("utf-8", errors="replace"))
print(f"Exit code: {proc.returncode}")
