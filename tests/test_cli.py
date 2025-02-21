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
    result = runner.invoke(cli, ["company", "--number", "2"])
    assert result.exit_code == 0
    assert "Generating company number 1 out of 2" in result.stdout
    assert "Generating company number 2 out of 2" in result.stdout


@pytest.mark.cli
def test_invoice_items_number():
    result = runner.invoke(cli, ["invoice-items", "--number", "1"])
    assert result.exit_code == 0
    assert "Generated 10 invoice items" in result.stdout
    assert "New invoice items" in result.stdout


@pytest.mark.cli
def test_invoice_number():
    result = runner.invoke(cli, ["invoice", "--number", "2"])
    assert result.exit_code == 0
    assert "Generating invoice 1 out of 2" in result.stdout
    assert "Generating invoice 2 out of 2" in result.stdout
