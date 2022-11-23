from __future__ import annotations

import typing

from rest_framework import serializers, viewsets
from taggit.serializers import TaggitSerializer, TagListSerializerField

from blog.models import Post

if typing.TYPE_CHECKING:
    from typing import Type

    from django.db.models import QuerySet


class PostsSerializer(TaggitSerializer, serializers.ModelSerializer[Post]):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        exclude = ("content", "last_modified")


class PostDetailSerializer(TaggitSerializer, serializers.ModelSerializer[Post]):
    tags = TagListSerializerField()

    class Meta:
        model = Post
        fields = "__all__"


class PostViewSet(viewsets.ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    def get_serializer_class(self) -> Type[serializers.ModelSerializer[Post]]:
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "list":
            return PostsSerializer
        return NotImplemented

    def get_queryset(self) -> QuerySet[Post]:
        # TODO/FIXME: had no success with django-filters, so have tags filtering this naive way
        queryset = Post.objects.all()
        tags = self.request.query_params.get("tags")
        if tags:
            queryset = queryset.filter(tags__name__in=tags.split(",")).distinct()
        return queryset.order_by("-published")
