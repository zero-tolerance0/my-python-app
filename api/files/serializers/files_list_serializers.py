from rest_framework import serializers

from api.users.serializers import UserShortSerializer
from marathons.models import MarathonFile


class MarathonFilesListSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    created_date = serializers.DateTimeField(required=False)
    author = serializers.CharField(required=False)
    size = serializers.FloatField(required=False)
    url = serializers.CharField(required=False)
    thumbnail = serializers.URLField(required=False)
    file_type = serializers.CharField(required=False)
    source_class = serializers.CharField(required=False)
    source_obj_id = serializers.SerializerMethodField()

    def get_source_obj_id(self, value):
        try:
            return value.source[0].id
        except:
            return 0


class MarathonFilesListSerializerNew(serializers.ModelSerializer):
    author = UserShortSerializer(required=False, read_only=True)
    attachment_type = serializers.SerializerMethodField()
    source_class = serializers.SerializerMethodField(method_name='get_content_object_class')

    class Meta:
        model = MarathonFile
        fields = [
            "id",
            "author",
            "marathon",
            "name",
            "created_date",
            "size",
            "url",
            "thumbnail",
            "file_type",
            "attachment_type",
            "source_class",
        ]

    def get_attachment_type(self, value):
        if value.attachment_type:
            return value.get_attachment_type_display()
        return ""

    def get_content_object_class(self, value):
        if value.content_type:
            return value.content_type.model
        return ""
