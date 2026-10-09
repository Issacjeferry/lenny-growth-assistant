from unittest.mock import AsyncMock

import pytest

from packages.agent.artifacts import sanitize_html
from packages.agent.grounding import cited_sources, route
from packages.agent.runtime import generate
from packages.retrieval.engine import Evidence
from packages.shared.config import Settings
from packages.shared.errors import ProviderUnavailableError


def evidence():
    return Evidence(
        id="one",
        title="Synthetic test episode",
        guest="Test Guest",
        url="https://example.com/test",
        excerpt="Test evidence",
        distance=0.2,
        timestamp_seconds=90,
    )


def test_fabricated_source_ids_reject_entire_answer():
    assert not cited_sources("Advice [S1] and invented evidence [S2]", [evidence()])
    assert not cited_sources("Advice without a citation", [evidence()])
    assert cited_sources("Advice [S1]", [evidence()]) == [evidence()]


@pytest.mark.parametrize(
    "payload",
    [
        "<script>alert(1)</script>",
        '<img src="https://evil.test" onerror="alert(1)">',
        '<iframe src="https://evil.test"></iframe>',
        '<svg onload="alert(1)"></svg>',
        '<meta http-equiv="refresh" content="0;url=https://evil.test">',
        '<form action="https://evil.test"><input></form>',
        '<a href="javascript:alert(1)" onclick="alert(1)">click</a>',
    ],
)
def test_html_removes_active_content_and_navigation(payload):
    result = sanitize_html(payload + "<h1>Safe heading</h1>")
    assert "<h1>Safe heading</h1>" in result
    for unsafe in (
        "<script",
        "<iframe",
        "<svg",
        "<form",
        "<input",
        "onerror=",
        "onclick=",
        "javascript:",
        "https://evil.test",
        'http-equiv="refresh"',
    ):
        assert unsafe not in result
    assert "default-src 'none'" in result


def test_html_retains_css_but_has_network_policy():
    result = sanitize_html("<style>h1{color:red}</style><h1>Title</h1>")
    assert "h1{color:red}" in result
    assert "style-src 'unsafe-inline'" in result


def test_explicit_skill_wins_over_keyword_routing():
    assert route("Make an HTML brief", "ship30") == "ship30"
    assert route("Write a Ship 30 essay", "qa") == "ship30"
    assert route("What is HTML onboarding?", "qa") == "qa"


@pytest.mark.asyncio
async def test_cloud_requires_explicit_model_and_key():
    with pytest.raises(ProviderUnavailableError) as exc:
        await generate("system", "prompt", "anthropic", Settings(_env_file=None))
    assert exc.value.error_code == "PROVIDER_NOT_CONFIGURED"


@pytest.mark.asyncio
async def test_model_timeout_kills_process(monkeypatch):
    import asyncio
    from unittest.mock import MagicMock

    process = MagicMock(returncode=None)
    process.communicate = AsyncMock(side_effect=[TimeoutError(), (b"", b"")])
    monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=process))
    with pytest.raises(ProviderUnavailableError) as exc:
        await generate("system", "prompt", "ollama", Settings(_env_file=None))
    assert exc.value.error_code == "MODEL_TIMEOUT"
    process.kill.assert_called_once()
