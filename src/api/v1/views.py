import uuid

import structlog

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from structlog.contextvars import bound_contextvars

from api.v1.serializers import InSummarySerializer, OutSummarySerializer
from services.summarise_excel.column_row_finder import ExcelColumnRowFinder
from services.summarise_excel.exceptions import BaseExcelSummaryError
from services.summarise_excel.file_readers import ExcelFileReader
from services.summarise_excel.row_converter import ExcelRowConverter
from services.summarise_excel.row_processors import ExcelRowProcessor
from services.summarise_excel.summary_generator import ExcelSummaryGenerator
from services.summarise_excel.value_processors import ExcelValueProcessor


logger = structlog.getLogger(__name__)


class ExcelSummaryView(APIView):
    @extend_schema(
        request=InSummarySerializer,
        responses=OutSummarySerializer,
        description="Upload an Excel file and generate column-wise summaries (sum and avg).",
    )
    def post(self, request: Request) -> Response:
        with bound_contextvars(request_data=request.data, correlation_id=str(uuid.uuid4())):
            in_serializer = InSummarySerializer(data=request.data)
            in_serializer.is_valid(raise_exception=True)
            file_reader = ExcelFileReader(file=in_serializer.validated_data["file"])
            value_processor = ExcelValueProcessor()
            row_converter = ExcelRowConverter()
            column_row_finder = ExcelColumnRowFinder()
            row_processor = ExcelRowProcessor(value_processor=value_processor)
            generator = ExcelSummaryGenerator(
                file_reader=file_reader,
                row_converter=row_converter,
                column_row_finder=column_row_finder,
                row_processor=row_processor,
            )
            try:
                summary = generator.generate(column_names=in_serializer.validated_data["column_names"])
            except BaseExcelSummaryError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"detail": e.detail})
            except Exception:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            out_serializer = OutSummarySerializer(
                {
                    "file": in_serializer.validated_data["file"].name,
                    "summary": summary,
                }
            )
        return Response(out_serializer.data)
