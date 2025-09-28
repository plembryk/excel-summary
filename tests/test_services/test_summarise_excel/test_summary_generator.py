from decimal import Decimal
from unittest.mock import MagicMock, call

import pytest

from services.summarise_excel.column_row_finder import BaseColumnRowFinder
from services.summarise_excel.file_readers import BaseFileReader
from services.summarise_excel.row_converter import BaseRowConverter, UnconvertibleRowError
from services.summarise_excel.row_processors import BaseRowProcessor, UnprocessableRowError
from services.summarise_excel.summary_generator import ColumnResult, ExcelSummaryGenerator


class TestColumnResult:
    def test_add(self):
        name = "name"
        column_result = ColumnResult(name=name)
        value = Decimal("2")
        column_result.add(value=value)

        assert column_result.count == 1
        assert column_result.total_value == value

    def test_calculate_when_count_is_zero(self):
        name = "name"
        column_result = ColumnResult(name=name)
        calculated_result = column_result.calculate()

        assert calculated_result == {
            "column": name,
            "sum": "N/A",
            "avg": "N/A",
        }

    def test_calculate(self):
        name = "name"
        column_result = ColumnResult(name=name)
        column_result.count = 2
        column_result.total_value = Decimal("5")
        calculated_result = column_result.calculate()

        assert calculated_result == {
            "column": name,
            "sum": str(Decimal("5")),
            "avg": str(Decimal("5") / 2),
        }


@pytest.fixture
def row_processor_mock():
    return MagicMock(spec=BaseRowProcessor)


@pytest.fixture
def row_converter_mock():
    return MagicMock(spec=BaseRowConverter)


@pytest.fixture
def file_reader_mock():
    return MagicMock(spec=BaseFileReader)


@pytest.fixture
def column_row_finder_mock():
    return MagicMock(spec=BaseColumnRowFinder)


@pytest.fixture
def excel_summary_generator(row_converter_mock, file_reader_mock, column_row_finder_mock, row_processor_mock):
    return ExcelSummaryGenerator(
        row_processor=row_processor_mock,
        row_converter=row_converter_mock,
        file_reader=file_reader_mock,
        column_row_finder=column_row_finder_mock,
    )


class TestExcelSummaryGenerator:
    def test_generate(
        self,
        row_converter_mock,
        file_reader_mock,
        column_row_finder_mock,
        row_processor_mock,
        excel_summary_generator,
    ):
        column_name_1 = "column_1"
        column_row = [column_name_1, "column_2"]
        row_number = 1
        column_row_finder_mock.find.return_value = column_row, 1

        row = (1, 2)
        file_reader_mock.iter_rows.return_value = [row]
        expected_column_to_index_mapper = {column_name_1: 0}
        converted_value = Decimal("2")
        row_converter_mock.convert.return_value = {column_name_1: converted_value}

        processed_value = Decimal(1)
        row_processor_mock.process.return_value = {column_name_1: processed_value}

        column_names = [column_name_1]
        result = excel_summary_generator.generate(column_names=column_names)
        column_row_finder_mock.find.assert_called_with(column_names=column_names, file_reader=file_reader_mock)
        file_reader_mock.iter_rows.assert_called_once_with(min_row=row_number + 1)
        row_converter_mock.convert.assert_called_once_with(row=row, index_mapping=expected_column_to_index_mapper)
        row_processor_mock.process.assert_called_once_with(row_dict={column_name_1: converted_value})

        assert result == [{"column": column_name_1, "sum": str(processed_value), "avg": str(processed_value)}]

    def test_generate_when_unconvertible_row(
        self,
        row_converter_mock,
        file_reader_mock,
        column_row_finder_mock,
        row_processor_mock,
        excel_summary_generator,
    ):
        column_name_1 = "column_1"
        column_row = [column_name_1, "column_2"]
        row_number = 1
        column_row_finder_mock.find.return_value = column_row, 1

        row = (1, 2)
        file_reader_mock.iter_rows.return_value = [row]
        expected_column_to_index_mapper = {column_name_1: 0}
        row_converter_mock.convert.side_effect = UnconvertibleRowError

        column_names = [column_name_1]
        result = excel_summary_generator.generate(column_names=column_names)
        row_processor_mock.process.assert_not_called()
        column_row_finder_mock.find.assert_called_with(column_names=column_names, file_reader=file_reader_mock)
        file_reader_mock.iter_rows.assert_called_once_with(min_row=row_number + 1)
        row_converter_mock.convert.assert_called_once_with(row=row, index_mapping=expected_column_to_index_mapper)

        assert result == [{"column": column_name_1, "sum": "N/A", "avg": "N/A"}]

    def test_generate_when_one_unconvertible_row_and_one_row_convertible(
        self,
        row_converter_mock,
        file_reader_mock,
        column_row_finder_mock,
        row_processor_mock,
        excel_summary_generator,
    ):
        column_name_1 = "column_1"
        column_row = [column_name_1, "column_2"]
        row_number = 1
        column_row_finder_mock.find.return_value = column_row, 1

        row_1 = (1, 2)
        row_2 = (3, 4)
        file_reader_mock.iter_rows.return_value = [row_1, row_2]
        expected_column_to_index_mapper = {column_name_1: 0}
        converted_value = Decimal("2")
        row_converter_mock.convert.side_effect = [UnconvertibleRowError, {column_name_1: converted_value}]

        processed_value = Decimal(1)
        row_processor_mock.process.return_value = {column_name_1: processed_value}

        column_names = [column_name_1]
        result = excel_summary_generator.generate(column_names=column_names)
        column_row_finder_mock.find.assert_called_with(column_names=column_names, file_reader=file_reader_mock)
        file_reader_mock.iter_rows.assert_called_once_with(min_row=row_number + 1)
        row_converter_mock.convert.assert_has_calls(
            [
                call(row=row_1, index_mapping=expected_column_to_index_mapper),
                call(row=row_2, index_mapping=expected_column_to_index_mapper),
            ]
        )
        row_processor_mock.process.assert_called_once_with(row_dict={column_name_1: converted_value})

        assert result == [{"column": column_name_1, "sum": str(processed_value), "avg": str(processed_value)}]

    def test_generate_when_unprocessable_row(
        self,
        row_converter_mock,
        file_reader_mock,
        column_row_finder_mock,
        row_processor_mock,
        excel_summary_generator,
    ):
        column_name_1 = "column_1"
        column_row = [column_name_1, "column_2"]
        row_number = 1
        column_row_finder_mock.find.return_value = column_row, 1

        row = (1, 2)
        file_reader_mock.iter_rows.return_value = [row]
        expected_column_to_index_mapper = {column_name_1: 0}
        converted_value = Decimal("2")
        row_converter_mock.convert.return_value = {column_name_1: converted_value}

        row_processor_mock.process.side_effect = UnprocessableRowError

        column_names = [column_name_1]
        result = excel_summary_generator.generate(column_names=column_names)
        column_row_finder_mock.find.assert_called_with(column_names=column_names, file_reader=file_reader_mock)
        file_reader_mock.iter_rows.assert_called_once_with(min_row=row_number + 1)
        row_converter_mock.convert.assert_called_once_with(row=row, index_mapping=expected_column_to_index_mapper)
        row_processor_mock.process.assert_called_once_with(row_dict={column_name_1: converted_value})

        assert result == [{"column": column_name_1, "sum": "N/A", "avg": "N/A"}]

    def test_generate_when_one_unprocessable_row_and_one_row_processable(
        self,
        row_converter_mock,
        file_reader_mock,
        column_row_finder_mock,
        row_processor_mock,
        excel_summary_generator,
    ):
        column_name_1 = "column_1"
        column_row = [column_name_1, "column_2"]
        row_number = 1
        column_row_finder_mock.find.return_value = column_row, 1

        row_1 = (1, 2)
        row_2 = (3, 4)
        file_reader_mock.iter_rows.return_value = [row_1, row_2]
        expected_column_to_index_mapper = {column_name_1: 0}
        converted_value = Decimal("2")
        row_converter_mock.convert.return_value = {column_name_1: converted_value}

        processed_value = Decimal(1)
        row_processor_mock.process.side_effect = [UnprocessableRowError, {column_name_1: processed_value}]

        column_names = [column_name_1]
        result = excel_summary_generator.generate(column_names=column_names)
        column_row_finder_mock.find.assert_called_with(column_names=column_names, file_reader=file_reader_mock)
        file_reader_mock.iter_rows.assert_called_once_with(min_row=row_number + 1)
        row_converter_mock.convert.assert_has_calls(
            [
                call(row=row_1, index_mapping=expected_column_to_index_mapper),
                call(row=row_2, index_mapping=expected_column_to_index_mapper),
            ]
        )
        row_processor_mock.process.assert_has_calls(
            [call(row_dict={column_name_1: converted_value}), call(row_dict={column_name_1: converted_value})]
        )

        assert result == [{"column": column_name_1, "sum": str(processed_value), "avg": str(processed_value)}]
