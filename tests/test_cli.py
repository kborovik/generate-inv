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
    assert "ANTHROPIC_API_KEY" in result.stdout


@pytest.mark.cli
def test_settings_save():
    result = runner.invoke(cli, ["settings", "--save"])
    assert result.exit_code == 0


@pytest.mark.cli
def test_company_number():
    result = runner.invoke(cli, ["company", "--generate", "1"])
    assert result.exit_code == 0


@pytest.mark.cli
def test_invoice_items_list():
    result = runner.invoke(cli, ["invoice-items", "--list"])
    assert result.exit_code == 0


@pytest.mark.cli
def test_invoice_items_number():
    result = runner.invoke(cli, ["invoice-items", "--generate", "1"])
    assert result.exit_code == 0
    assert "Generated 5 invoice items" in result.stdout
    assert "New invoice items" in result.stdout


@pytest.mark.cli
def test_invoice_number():
    result = runner.invoke(cli, ["invoice", "--generate", "1"])
    assert result.exit_code == 0
