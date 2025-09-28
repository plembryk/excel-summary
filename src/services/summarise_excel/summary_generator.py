import abc

from decimal import Decimal
from typing import Any, Sequence

import structlog

from services.summarise_excel.column_row_finder import BaseColumnRowFinder
from services.summarise_excel.file_readers import BaseFileReader
from services.summarise_excel.row_converter import BaseRowConverter, UnconvertibleRowError
from services.summarise_excel.row_processors import BaseRowProcessor, UnprocessableRowError


logger = structlog.getLogger(__name__)


class ColumnResult:
    def __init__(self, name: str) -> None:
        self.name = name
        self.total_value: Decimal = Decimal(0)
        self.count: int = 0

    def add(self, value: Decimal) -> None:
        self.total_value += value
        self.count += 1

    def calculate(self) -> dict[str, str]:
        return {
            "column": self.name,
            "sum": str(self.total_value) if self.count else "N/A",
            "avg": str(self.total_value / self.count) if self.count else "N/A",
        }


class BaseSummaryGenerator(abc.ABC):
    @abc.abstractmethod
    def generate(self, column_names: Sequence[str]) -> list[dict[str, Any]]: ...


class ExcelSummaryGenerator(BaseSummaryGenerator):
    def __init__(
        self,
        row_processor: BaseRowProcessor,
        row_converter: BaseRowConverter,
        file_reader: BaseFileReader,
        column_row_finder: BaseColumnRowFinder,
    ) -> None:
        self.row_processor = row_processor
        self.row_converter = row_converter
        self.file_reader = file_reader
        self.column_row_finder = column_row_finder

    def generate(self, column_names: Sequence[str]) -> list[dict[str, Any]]:
        logger.debug("Generating summary", column_names=column_names)
        column_row, row_number = self.column_row_finder.find(column_names=column_names, file_reader=self.file_reader)

        column_to_index_mapper = {
            column_name: column_index
            for column_index, column_name in enumerate(column_row)
            if column_name in column_names
        }
        column_results = {column_name: ColumnResult(name=column_name) for column_name in column_names}

        for row in self.file_reader.iter_rows(min_row=row_number + 1):
            try:
                converted_row = self.row_converter.convert(row=row, index_mapping=column_to_index_mapper)
            except UnconvertibleRowError:
                continue
            try:
                processed_row = self.row_processor.process(row_dict=converted_row)
            except UnprocessableRowError:
                continue

            for column_name, row_result in processed_row.items():
                column_results[column_name].add(value=row_result)
        logger.debug("Finished generating summary")
        return [column_result.calculate() for column_result in column_results.values()]
