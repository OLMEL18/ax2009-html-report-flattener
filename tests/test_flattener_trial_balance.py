from pathlib import Path

from ax2009_html_report_flattener.flattener import convert_html_to_flat_table


FIXTURES = Path(__file__).parent / "fixtures"


def test_gl_trial_balance_combines_multi_row_headers():
    table = convert_html_to_flat_table(FIXTURES / "gl_trial_balance.html")

    assert table.stats.exported_rows == 2
    assert "Счет Код" in table.headers
    assert "Обороты за период Кредит" in table.headers
    assert table.rows[0]["Сальдо на начало периода Дебет"] == 1000.0
    assert table.rows[1]["Сальдо на конец периода Кредит"] == 400.0


def test_vendor_trial_balance_carries_supplier_and_gl_context():
    table = convert_html_to_flat_table(FIXTURES / "vendor_trial_balance.html")

    assert table.stats.exported_rows == 2
    assert table.rows[0]["Счет поставщика"] == "VEND-FAKE-77"
    assert table.rows[0]["Имя"] == "Synthetic Vendor Balance"
    assert table.rows[0]["Счет ГК"] == "GL-FAKE-631"
    assert table.rows[0]["Документ"] == "DOC-FAKE-1"
    assert table.rows[1]["Кредит"] == 2500.0
