from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from api.files.serializers import (
    MarathonFilesListSerializer,
    MarathonFilesListSerializerNew
)
from marathons.models import Post, Task, TaskResults

from marathons.models.marathon_file import MarathonFileNotinDB, MarathonFile
from utils.validators import MarathonValidators


class MarathonFilesListView(generics.GenericAPIView):
    serializer_class = MarathonFilesListSerializer

    def get(self, request, *args, **kwargs):
        marathon = self.check_validation(request, *args, **kwargs)
        posts = marathon.post.all()
        tasks = marathon.tasks.all()
        task_results = None

        converted_posts = self.convert_posts_to_general(request=request, posts=posts)
        converted_tasks = self.convert_tasks_to_general(request=request, tasks=tasks)
        general_list = []
        general_list.extend(converted_posts)
        general_list.extend(converted_tasks)
        ser = self.serializer_class(general_list, many=True)
        response = ser.data
        return Response({"count": len(response), "result": response})

    def check_validation(self, request, *args, **kwargs):
        marathon = MarathonValidators.is_valid_marathone(marathon_id=kwargs.get('marathon_id'))
        if not MarathonValidators.is_participant(user_id=request.user.id, marathon_id=marathon.id):
            raise PermissionDenied('you are not the participant of the marathon')
        return marathon

    def convert_posts_to_general(self, request, posts):
        from sorl.thumbnail import get_thumbnail
        """
        this method converts posts queryset to general list, by which we can make unique list with tasks and task_results
        """
        result = []
        for post in posts:
            post_name = post.get_name()
            post_attachment_url = post.get_attachment_url()
            if post_attachment_url:
                post_attachment_absolute_url = request.build_absolute_uri(post_attachment_url)
                thumbnail = get_thumbnail(post.attachment.url, '132x132', crop='center', quality=99)
                thumbnail_absolute_url = request.build_absolute_uri(thumbnail)
                marathon_file_not_in_db = MarathonFileNotinDB(
                    name=post_name,
                    created_date=post.created_date,
                    author=post.get_author(),
                    size=post.get_attachment_size(),
                    url=post_attachment_absolute_url,
                    thumbnail=thumbnail,  # fix. this is static
                    file_type=post.get_attachment_type(),
                    source=post,
                )
                result.append(marathon_file_not_in_db)
        return result

    def convert_tasks_to_general(self, request, tasks):
        result = []
        for task in tasks:
            author = None
            attachment_url = task.get_attachment_url(

            )
            if attachment_url:
                attachment_url = request.build_absolute_uri(attachment_url)
                if task.get_task_creator():
                    author = task.get_task_creator()[0]
                marathon_file_not_in_db = MarathonFileNotinDB(
                    name=task.name,
                    created_date=task.created_date,
                    author=author,
                    size=task.get_attachment_size(),
                    url=attachment_url,
                    thumbnail="we",  # fix. this is static
                    file_type=task.get_attachment_type(),
                    source=task,
                )
                result.append(marathon_file_not_in_db)
        return result


class MarathonFilesListViewNew(generics.ListAPIView):
    serializer_class = MarathonFilesListSerializerNew

    def get_queryset(self):
        post_model = ContentType.objects.get_for_model(Post)
        task_model = ContentType.objects.get_for_model(Task)
        task_result_model = ContentType.objects.get_for_model(TaskResults)
        return MarathonFile.objects. \
            filter(marathon_id=self.kwargs.get('marathon_id')). \
            filter(Q(content_type=post_model) | Q(content_type=task_model) | Q(content_type=task_result_model)). \
            order_by('-id')

    def get(self, request, *args, **kwargs):
        self.check_validation(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def check_validation(self, request, *args, **kwargs):
        marathon = MarathonValidators.is_valid_marathone(marathon_id=kwargs.get('marathon_id'))
        if not (MarathonValidators.is_participant(user_id=request.user.id, marathon_id=marathon.id) or MarathonValidators.is_marathon_owner(user_id=request.user.id,
                                                                                                                                            marathon_id=marathon.id)):
            raise PermissionDenied('you are neither the owner nor participan of the marathon')
        return marathon
