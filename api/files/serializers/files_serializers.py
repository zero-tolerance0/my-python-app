from django.conf import settings
from rest_framework import serializers

from api.users.serializers import UserShortSerializer
from marathons.models import MarathonFile


class MarathonFilesSerializer(serializers.ModelSerializer):
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


class MarathonFilesAttachmentCreateSerializer(serializers.ModelSerializer):
    """
    this serializer is for the cases when following types of objects are created.
    types = [
    Comment,

    ]
    """
    attachment_type = serializers.SerializerMethodField()
    source_class = serializers.SerializerMethodField(method_name='get_content_object_class')
    url = serializers.SerializerMethodField()
    class Meta:
        model = MarathonFile
        fields = [
            "id",
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

    def get_url(self,value):
        request = self.context.get('request')
        if request and value.get_fullurl_url():
            return request.build_absolute_uri(value.get_fullurl_url())
        return value.get_fullurl_url()
