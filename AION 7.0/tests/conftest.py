import pytest
from unittest.mock import MagicMock

from src.config import Settings
from src.api.deepseek_client import DeepSeekClient


@pytest.fixture
def settings():
    s = Settings()
    s.deepseek_api_key = "test-key"
    return s


@pytest.fixture
def llm_mock():
    mock = MagicMock(spec=DeepSeekClient)
    mock.chat.return_value = "Analise concluida com sucesso."
    mock.health_check.return_value = True
    return mock


@pytest.fixture
def llm():
    return None
