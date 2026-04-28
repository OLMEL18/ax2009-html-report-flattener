from pathlib import Path

from ax2009_html_report_flattener.flattener import convert_html_to_flat_table


FIXTURES = Path(__file__).parent / "fixtures"


def test_inventory_warehouse_extracts_flat_rows_and_skips_totals():
    table = convert_html_to_flat_table(FIXTURES / "inventory_warehouse.html")

    assert table.headers == [
        "Код номенклатуры",
        "Наименование номенклатуры",
        "Склад",
        "Количество",
        "Сумма затрат",
    ]
    assert table.stats.exported_rows == 2
    assert table.rows[0]["Код номенклатуры"] == "* FAKE-001"
    assert table.rows[0]["Количество"] == 55440.0
    assert table.rows[0]["Сумма затрат"] == 1068940.35
    assert all(row["Код номенклатуры"] != "Итого" for row in table.rows)


def test_inventory_group_extracts_rows_and_ignores_repeated_header():
    table = convert_html_to_flat_table(FIXTURES / "inventory_group.html")

    assert table.stats.exported_rows == 2
    assert table.rows[0]["Номенклатурная группа"] == "FAKE-GROUP-A"
    assert table.rows[1]["Код номенклатуры"] == "* FAKE-102"
    assert table.rows[1]["Значение"] == 5000.0
