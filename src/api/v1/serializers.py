from rest_framework import serializers


class InSummarySerializer(serializers.Serializer):
    file = serializers.FileField()
    column_names = serializers.ListField(child=serializers.CharField())


class OutSummarySerializer(serializers.Serializer):
    file = serializers.CharField()
    summary = serializers.ListField(child=serializers.DictField())
