import abc

from typing import Any, Mapping, Sequence

import structlog


logger = structlog.getLogger(__name__)


class UnconvertibleRowError(Exception):
    pass


class BaseRowConverter(abc.ABC):
    @abc.abstractmethod
    def convert(self, row: Sequence, index_mapping: Mapping[str, int]) -> Mapping[str, Any]: ...


class ExcelRowConverter(BaseRowConverter):
    def convert(self, row: Sequence, index_mapping: Mapping[str, int]) -> Mapping[str, Any]:
        logger.debug("Converting row", row=row, index_mapping=index_mapping)
        try:
            return {column_name: row[column_index] for column_name, column_index in index_mapping.items()}
        except IndexError:
            logger.warning("Unconvertible row", row=row, index_mapping=index_mapping)
            raise UnconvertibleRowError
