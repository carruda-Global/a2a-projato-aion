from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/office-addin", tags=["office_addin_commands"])

COMMANDS_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <script src="https://appsforoffice.microsoft.com/lib/1/hosted/office.js"></script>
</head>
<body>
  <script>
    Office.onReady(() => { });
  </script>
</body>
</html>
"""

@router.get("/commands.html", response_class=HTMLResponse)
async def commands():
    return COMMANDS_HTML
