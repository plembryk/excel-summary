from pathlib import Path
from typing import Any, Iterable

import pytest

from openpyxl import Workbook
from rest_framework.test import APIClient


@pytest.fixture
def sample_excel_file_factory(tmp_path):
    def _builder(data: Iterable[Any], file_name: str = "test.xlsx") -> Path:
        file_path = tmp_path / file_name
        wb = Workbook()
        ws = wb.active
        for row in data:
            ws.append(row)
        wb.save(file_path)
        wb.close()
        return file_path

    return _builder


@pytest.fixture
def api_client():
    return APIClient()
