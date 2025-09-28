from rest_framework import status


class TestExcelSummaryView:
    def test_excel_summary_one_column_row_and_one_data_row(self, api_client, sample_excel_file_factory):
        url = "/api/v1/excel-summary/"
        file_name = "test.xlsx"
        sample_excel_file_path = sample_excel_file_factory(data=[["a", "b", "c"], [1, 2, 3]], file_name=file_name)

        with open(sample_excel_file_path, "rb") as file:
            data = {
                "file": file,
                "column_names": ["a", "b"],
            }
            response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "file": file_name,
            "summary": [{"column": "a", "sum": "1", "avg": "1"}, {"column": "b", "sum": "2", "avg": "2"}],
        }

    def test_excel_summary_two_data_rows(self, api_client, sample_excel_file_factory):
        url = "/api/v1/excel-summary/"
        file_name = "test.xlsx"
        sample_excel_file_path = sample_excel_file_factory(
            data=[["a", "b", "c"], [1, 2, 3], [1, 2, 3]], file_name=file_name
        )

        with open(sample_excel_file_path, "rb") as file:
            data = {
                "file": file,
                "column_names": ["a", "b"],
            }
            response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "file": file_name,
            "summary": [{"column": "a", "sum": "2", "avg": "1"}, {"column": "b", "sum": "4", "avg": "2"}],
        }

    def test_excel_summary_two_data_rows_from_which_one_is_unprocessable(self, api_client, sample_excel_file_factory):
        url = "/api/v1/excel-summary/"
        file_name = "test.xlsx"
        sample_excel_file_path = sample_excel_file_factory(
            data=[["a", "b", "c"], [1, None, None], [1, 2, 3]], file_name=file_name
        )

        with open(sample_excel_file_path, "rb") as file:
            data = {
                "file": file,
                "column_names": ["a", "b"],
            }
            response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "file": file_name,
            "summary": [{"column": "a", "sum": "1", "avg": "1"}, {"column": "b", "sum": "2", "avg": "2"}],
        }

    def test_excel_summary_when_zero_rows_are_processable(self, api_client, sample_excel_file_factory):
        url = "/api/v1/excel-summary/"
        file_name = "test.xlsx"
        sample_excel_file_path = sample_excel_file_factory(
            data=[["a", "b", "c"], [1, None, None], [None, 2, 3]], file_name=file_name
        )

        with open(sample_excel_file_path, "rb") as file:
            data = {
                "file": file,
                "column_names": ["a", "b"],
            }
            response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "file": file_name,
            "summary": [{"column": "a", "sum": "N/A", "avg": "N/A"}, {"column": "b", "sum": "N/A", "avg": "N/A"}],
        }

    def test_excel_summary_when_column_row_cannot_be_found(self, api_client, sample_excel_file_factory):
        url = "/api/v1/excel-summary/"
        file_name = "test.xlsx"
        sample_excel_file_path = sample_excel_file_factory(
            data=[["a", "b", "c"], [1, None, None], [None, 2, 3]], file_name=file_name
        )

        with open(sample_excel_file_path, "rb") as file:
            data = {
                "file": file,
                "column_names": ["ab", "ba"],
            }
            response = api_client.post(url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Column row cannot be found"
