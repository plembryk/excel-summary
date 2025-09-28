class BaseExcelSummaryError(Exception):
    """Base exception for summary generator"""

    def __init__(self, detail: str) -> None:
        self.detail = detail


class ColumnRowNotFoundError(BaseExcelSummaryError):
    def __init__(self) -> None:
        super().__init__("Column row cannot be found")


class CannotReadFileError(BaseExcelSummaryError):
    """Raised when a file cannot be read"""

    def __init__(self) -> None:
        super().__init__("Cannot read file")
