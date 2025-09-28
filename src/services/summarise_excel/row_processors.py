import abc

from typing import Any, Mapping

import structlog

from services.summarise_excel.value_processors import BaseValueProcessor, ColumnValueUnprocessableError


logger = structlog.getLogger(__name__)


class UnprocessableRowError(Exception):
    pass


class BaseRowProcessor(abc.ABC):
    @abc.abstractmethod
    def process(self, row_dict: Mapping[str, Any]) -> dict[str, Any]: ...


class ExcelRowProcessor(BaseRowProcessor):
    def __init__(self, value_processor: BaseValueProcessor) -> None:
        self.value_processor = value_processor

    def process(self, row_dict: Mapping[str, Any]) -> dict[str, Any]:
        logger.debug("Processing row", row_dict=row_dict)
        try:
            return {
                column_name: self.value_processor.process(column_value)
                for column_name, column_value in row_dict.items()
            }
        except (ColumnValueUnprocessableError, IndexError):
            logger.warning("Failed to process row", row_dict=row_dict, exc_info=True)
            raise UnprocessableRowError
