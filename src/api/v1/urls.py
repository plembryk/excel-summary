from django.urls import path

from api.v1.views import ExcelSummaryView


urlpatterns = [
    path("excel-summary/", ExcelSummaryView.as_view(), name="excel-summary"),
]
