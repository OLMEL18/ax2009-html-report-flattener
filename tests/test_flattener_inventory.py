from pathlib import Path

from ax2009_html_report_flattener.flattener import cleanup_technical_columns, convert_html_to_flat_table


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
    assert not any(header.startswith("Column") for header in table.headers)
    assert all(row["Код номенклатуры"] != "Итого" for row in table.rows)


def test_inventory_group_extracts_rows_and_ignores_repeated_header():
    table = convert_html_to_flat_table(FIXTURES / "inventory_group.html")

    assert table.stats.exported_rows == 2
    assert table.rows[0]["Номенклатурная группа"] == "FAKE-GROUP-A"
    assert table.rows[1]["Код номенклатуры"] == "* FAKE-102"
    assert table.rows[1]["Значение"] == 5000.0


def test_cleanup_removes_marker_only_technical_columns():
    headers, rows, warnings = cleanup_technical_columns(
        ["Column_1", "Код номенклатуры", "Количество"],
        [
            {"Column_1": "*", "Код номенклатуры": "FAKE-001", "Количество": 10.0},
            {"Column_1": " ", "Код номенклатуры": "FAKE-002", "Количество": 20.0},
        ],
    )

    assert headers == ["Код номенклатуры", "Количество"]
    assert rows[0] == {"Код номенклатуры": "FAKE-001", "Количество": 10.0}
    assert rows[0]["Количество"] == 10.0
    assert warnings == []


def test_cleanup_keeps_meaningful_unnamed_column_with_warning():
    headers, rows, warnings = cleanup_technical_columns(
        ["Column_2", "Business"],
        [{"Column_2": "unexpected value", "Business": "kept"}],
    )

    assert headers == ["Column_2", "Business"]
    assert rows[0]["Column_2"] == "unexpected value"
    assert warnings == ["Unnamed technical column 'Column_2' contains data and was kept."]
