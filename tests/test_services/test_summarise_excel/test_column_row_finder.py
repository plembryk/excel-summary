from unittest.mock import MagicMock

import pytest

from services.summarise_excel.column_row_finder import ColumnRowNotFoundError, ExcelColumnRowFinder
from services.summarise_excel.file_readers import BaseFileReader


class TestExcelColumnRowFinder:
    def test_find_when_there_are_no_rows(self):
        file_reader = MagicMock(spec=BaseFileReader)
        file_reader.iter_rows.return_value = []
        finder = ExcelColumnRowFinder()
        columns_names = ["column_name"]

        with pytest.raises(ColumnRowNotFoundError):
            finder.find(file_reader=file_reader, column_names=columns_names)

    def test_find_when_column_name_is_not_present(self):
        file_reader = MagicMock(spec=BaseFileReader)
        file_reader.iter_rows.return_value = [["present_column_name"]]
        finder = ExcelColumnRowFinder()
        columns_names = ["not_present_column_name"]

        with pytest.raises(ColumnRowNotFoundError):
            finder.find(file_reader=file_reader, column_names=columns_names)

    def test_find_when_only_one_column_name_is_not_present(self):
        file_reader = MagicMock(spec=BaseFileReader)
        file_reader.iter_rows.return_value = [["present_column_name"]]
        finder = ExcelColumnRowFinder()
        columns_names = ["not_present_column_name", "present_column_name"]

        with pytest.raises(ColumnRowNotFoundError):
            finder.find(file_reader=file_reader, column_names=columns_names)

    def test_find(self):
        file_reader = MagicMock(spec=BaseFileReader)
        present_column_name_1 = "present_column_name_1"
        present_column_name_2 = "present_column_name_2"
        column_row = [present_column_name_1, present_column_name_2, "present_column_name_3"]
        file_reader.iter_rows.return_value = [column_row]
        finder = ExcelColumnRowFinder()
        columns_names = [present_column_name_1, present_column_name_2]

        row, row_number = finder.find(file_reader=file_reader, column_names=columns_names)

        assert row_number == 1
        assert row == column_row

    def test_find_when_column_row_is_not_first(self):
        file_reader = MagicMock(spec=BaseFileReader)
        present_column_name_1 = "present_column_name_1"
        present_column_name_2 = "present_column_name_2"
        not_column_row = [present_column_name_1]
        column_row = [present_column_name_1, present_column_name_2, "present_column_name_3"]
        file_reader.iter_rows.return_value = [not_column_row, column_row]
        finder = ExcelColumnRowFinder()
        columns_names = [present_column_name_1, present_column_name_2]

        row, row_number = finder.find(file_reader=file_reader, column_names=columns_names)

        assert row_number == 2
        assert row == column_row
