import pytest
from typer.testing import CliRunner

from generate_inv import cli

runner = CliRunner()


@pytest.mark.cli
def test_version():
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "Version:" in result.stdout


@pytest.mark.cli
def test_settings_list():
    result = runner.invoke(cli, ["settings", "--list"])
    assert result.exit_code == 0
    assert "PYDANTIC_AI_MODEL=claude-3-5-haiku-latest" in result.stdout


@pytest.mark.cli
def test_settings_save():
    result = runner.invoke(cli, ["settings", "--save"])
    assert result.exit_code == 0
