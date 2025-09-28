from unittest.mock import MagicMock, call

import pytest

from services.summarise_excel.row_processors import ExcelRowProcessor, UnprocessableRowError
from services.summarise_excel.value_processors import BaseValueProcessor, ColumnValueUnprocessableError


class TestExcelRowProcessor:
    def test_process(self):
        value_1 = 2
        value_2 = 3
        row_dict = {
            "column_1": value_1,
            "column_2": value_2,
        }
        value_processor_mock = MagicMock(spec=BaseValueProcessor)
        value_processor_mock.process.side_effect = lambda x: x
        processor = ExcelRowProcessor(value_processor=value_processor_mock)
        processed_row = processor.process(row_dict=row_dict)

        assert value_processor_mock.process.call_count == 2
        value_processor_mock.process.assert_has_calls(
            [call(value_1), call(value_2)],
            any_order=True,
        )
        assert processed_row == row_dict

    @pytest.mark.parametrize("error", [ColumnValueUnprocessableError, IndexError])
    def test_process_when_unprocessable_value(self, error):
        row_dict = {
            "column_1": 1,
            "column_2": 2,
        }
        value_processor_mock = MagicMock(spec=BaseValueProcessor)
        value_processor_mock.process.side_effect = error
        processor = ExcelRowProcessor(value_processor=value_processor_mock)

        with pytest.raises(UnprocessableRowError):
            processor.process(row_dict=row_dict)
