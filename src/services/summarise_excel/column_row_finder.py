import abc

from typing import Iterable, Tuple

import structlog

from services.summarise_excel.exceptions import ColumnRowNotFoundError
from services.summarise_excel.file_readers import BaseFileReader


logger = structlog.getLogger(__name__)


class BaseColumnRowFinder(abc.ABC):
    @abc.abstractmethod
    def find(self, file_reader: BaseFileReader, column_names: Iterable[str]) -> Tuple[Iterable, int]: ...


class ExcelColumnRowFinder(BaseColumnRowFinder):
    def find(self, file_reader: BaseFileReader, column_names: Iterable[str]) -> Tuple[Iterable, int]:
        logger.debug("Finding column row", column_names=column_names)
        column_names_set = set(column_names)
        for row_number, row in enumerate(file_reader.iter_rows(), start=1):
            stripped_row = [item.strip(" ") if isinstance(item, str) else item for item in row]

            if column_names_set.issubset(set(stripped_row)):
                logger.debug("Found column row", row_number=row_number, column_names=stripped_row)
                return stripped_row, row_number
        logger.warning("No column row found", column_names=column_names)
        raise ColumnRowNotFoundError
