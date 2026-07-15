import pytest
from src.config import Settings


@pytest.fixture
def settings():
    s = Settings()
    s.deepseek_api_key = "test-key"
    return s


@pytest.mark.unit
class TestOfficeAddin:
    def test_router_prefix(self):
        from app.routers.office_addin import router
        assert router.prefix == "/office-addin"

    def test_taskpane_contains_chat(self):
        from app.routers.office_addin import TASKPANE_HTML
        assert "SallesJam" in TASKPANE_HTML
        assert "sendMessage" in TASKPANE_HTML
        assert "analyzeSheet" in TASKPANE_HTML
        assert "office.js" in TASKPANE_HTML


@pytest.mark.unit
class TestGoogleAddon:
    def test_code_gs_exists(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "templates", "google-addon", "Code.gs")
        assert os.path.exists(path)
        content = open(path, encoding="utf-8").read()
        assert "onHomepage" in content
        assert "onGmailMessageOpen" in content
        assert "analyzeEmailLGPD" in content

    def test_appsscript_json_exists(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "templates", "google-addon", "appsscript.json")
        assert os.path.exists(path)
        content = open(path, encoding="utf-8").read()
        assert "SallesJam" in content


@pytest.mark.unit
class TestChromeExtension:
    def test_manifest_exists(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "chrome-extension", "manifest.json")
        assert os.path.exists(path)
        content = open(path, encoding="utf-8").read()
        assert "manifest_version" in content
        assert "SallesJam" in content

    def test_popup_files_exist(self):
        import os
        base = os.path.join(os.path.dirname(__file__), "..", "chrome-extension")
        assert os.path.exists(os.path.join(base, "popup.html"))
        assert os.path.exists(os.path.join(base, "popup.js"))
        assert os.path.exists(os.path.join(base, "content.js"))

    def test_content_js_has_relevant_sites(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "chrome-extension", "content.js")
        content = open(path, encoding="utf-8").read()
        assert "gov.br" in content


@pytest.mark.unit
class TestIndiaAgent:
    def test_router_prefix(self):
        from src.agents.india_multilingual_agent import router
        assert router.prefix == "/api/india"

    def test_system_prompt_defined(self):
        from src.agents.india_multilingual_agent import SYSTEM_PROMPT_IN
        assert "India" in SYSTEM_PROMPT_IN
        assert len(SYSTEM_PROMPT_IN) > 50


@pytest.mark.unit
class TestUAEGovAgent:
    def test_router_prefix(self):
        from src.agents.uae_government_agent import router
        assert router.prefix == "/api/uae"

    def test_system_prompt_defined(self):
        from src.agents.uae_government_agent import SYSTEM_PROMPT_UAE
        assert "UAE" in SYSTEM_PROMPT_UAE
        assert len(SYSTEM_PROMPT_UAE) > 50
