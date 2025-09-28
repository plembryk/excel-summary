import pytest

from services.summarise_excel.file_readers import ExcelFileReader


@pytest.fixture
def sample_data():
    return [
        ("id", "name", "age"),
        (1, "Blob", 3),
        (2, "Alice", 4),
        (None, None, None),
        (1, 2, None),
    ]


class TestExcelFileReader:
    def test_iter_rows_reads_all_rows(self, sample_excel_file_factory, sample_data):
        sample_excel_file_path = sample_excel_file_factory(sample_data)
        reader = ExcelFileReader(str(sample_excel_file_path))
        rows = list(reader.iter_rows())
        assert rows == sample_data

    def test_iter_rows_with_min_row(self, sample_excel_file_factory, sample_data):
        sample_excel_file_path = sample_excel_file_factory(sample_data)
        reader = ExcelFileReader(str(sample_excel_file_path))
        rows = list(reader.iter_rows(min_row=2))
        assert rows == sample_data[1:]

    def test_iter_rows_empty_file(self, sample_excel_file_factory):
        sample_excel_file_path = sample_excel_file_factory([])
        reader = ExcelFileReader(str(sample_excel_file_path))
        rows = list(reader.iter_rows())
        assert rows == []
