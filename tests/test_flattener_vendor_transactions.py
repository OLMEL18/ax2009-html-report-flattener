from pathlib import Path

from ax2009_html_report_flattener.flattener import convert_html_to_flat_table


FIXTURES = Path(__file__).parent / "fixtures"


def test_vendor_transactions_carry_forward_vendor_context():
    table = convert_html_to_flat_table(FIXTURES / "vendor_transactions.html")

    assert table.stats.exported_rows == 2
    assert table.headers[:2] == ["Счет поставщика", "Имя"]
    assert table.rows[0]["Счет поставщика"] == "VEND-FAKE-01"
    assert table.rows[0]["Имя"] == "Synthetic Vendor One"
    assert table.rows[1]["Операция"] == "OP-002"
    assert table.rows[1]["Кредит"] == 500.0
    assert table.rows[1]["Сумма в валюте"] == -500.0
