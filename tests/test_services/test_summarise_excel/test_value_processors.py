from decimal import Decimal

import pytest

from services.summarise_excel.value_processors import ColumnValueUnprocessableError, ExcelValueProcessor


class TestExcelValueProcessor:
    @pytest.mark.parametrize(
        ("value", "expected_value"),
        [
            [1, Decimal("1")],
            ["  2  ", Decimal("2")],
            ["2.333333333333333333", Decimal("2.333333333333333333")],
            [1.2, Decimal(1.2)],
            [Decimal("1.2"), Decimal("1.2")],
        ],
    )
    def test_process(self, value, expected_value):
        processor = ExcelValueProcessor()
        processed_value = processor.process(value)
        assert processed_value == expected_value

    @pytest.mark.parametrize(
        ("value", "supported_currencies", "expected_value"),
        [
            ["1$", ["$"], Decimal("1")],
            ["1$$", ["$"], Decimal("1")],
            ["$1", ["$"], Decimal("1")],
            ["$$1", ["$"], Decimal("1")],
            ["$$1##", ["$", "#"], Decimal("1")],
            ["$#1#$", ["$", "#"], Decimal("1")],
            ["1USD", ["USD"], Decimal("1")],
        ],
    )
    def test_process_with_supported_currencies(self, value, expected_value, supported_currencies):
        processor = ExcelValueProcessor(supported_currencies=supported_currencies)
        processed_value = processor.process(value)
        assert processed_value == expected_value

    @pytest.mark.parametrize("value", [None, "string"])
    def test_process_when_unprocessable_value(self, value):
        processor = ExcelValueProcessor()
        with pytest.raises(ColumnValueUnprocessableError):
            processor.process(value)
