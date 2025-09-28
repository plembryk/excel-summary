import pytest

from services.summarise_excel.row_converter import ExcelRowConverter, UnconvertibleRowError


class TestExcelRowConverter:
    def test_convert_when_all_columns(self):
        row = ("column_1_value", "column_2_value", "column_3_value")
        index_mapping = {"column_1": 0, "column_2": 1, "column_3": 2}
        converter = ExcelRowConverter()
        converted_row = converter.convert(row=row, index_mapping=index_mapping)
        assert converted_row == {
            "column_1": "column_1_value",
            "column_2": "column_2_value",
            "column_3": "column_3_value",
        }

    def test_convert_when_only_some_columns(self):
        row = ("column_1_value", "column_2_value", "column_3_value")
        index_mapping = {"column_1": 0, "column_3": 2}
        converter = ExcelRowConverter()
        converted_row = converter.convert(row=row, index_mapping=index_mapping)
        assert converted_row == {
            "column_1": "column_1_value",
            "column_3": "column_3_value",
        }

    def test_convert_when_empty_mapper(self):
        row = ("column_1_value", "column_2_value", "column_3_value")
        index_mapping = {}
        converter = ExcelRowConverter()
        converted_row = converter.convert(row=row, index_mapping=index_mapping)
        assert converted_row == {}

    def test_convert_when_row_unconvertible(self):
        row = ("column_1_value", "column_2_value", "column_3_value")
        index_mapping = {"column_1": 0, "column_4": 3}
        converter = ExcelRowConverter()

        with pytest.raises(UnconvertibleRowError):
            converter.convert(row=row, index_mapping=index_mapping)
