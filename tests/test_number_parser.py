from ax2009_html_report_flattener.number_parser import parse_localized_number


def test_parse_localized_numbers():
    assert parse_localized_number("55 440,0000") == 55440.0
    assert parse_localized_number("1 068 940,35") == 1068940.35
    assert parse_localized_number("-6 500,00") == -6500.0
    assert parse_localized_number("") == ""
    assert parse_localized_number("11.02.2020") == "11.02.2020"
