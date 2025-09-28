import abc

from decimal import Decimal, InvalidOperation
from typing import Any

import structlog


logger = structlog.getLogger(__name__)


class ColumnValueUnprocessableError(Exception):
    pass


class BaseValueProcessor(abc.ABC):
    @abc.abstractmethod
    def process(self, value: Any) -> Decimal: ...


class ExcelValueProcessor(BaseValueProcessor):
    def __init__(self, supported_currencies: list[str] | None = None):
        self.supported_currencies = supported_currencies or []

    def process(self, value: Any) -> Decimal:
        logger.debug("Processing value", value=value)
        value_to_convert = value
        if isinstance(value, str):
            logger.debug("Processing string value", value=value)
            value_to_convert = value.strip(" ").strip("".join(self.supported_currencies))
        try:
            return Decimal(value_to_convert)
        except (InvalidOperation, TypeError):
            logger.warning("Failed to process value", value=value, exc_info=True)
            raise ColumnValueUnprocessableError
