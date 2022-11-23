from __future__ import annotations

import typing

import pytest
from django.urls import reverse
from rest_framework import serializers

if typing.TYPE_CHECKING:
    from typing import List

    from django.test import Client

    from blog.models import Post


@pytest.mark.parametrize(
    "url", (reverse("api-root"), reverse("api-root", kwargs={"format": "json"}))
)
def test_swagger(url: str, client: Client) -> None:
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_list_posts_empty(client: Client) -> None:
    url = reverse("api-posts-list")
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        "count": 0,
        "next": None,
        "previous": None,
        "results": [],
    }


@pytest.mark.django_db
def test_get_post_404(client: Client) -> None:
    url = reverse("api-posts-detail", args=(1,))
    response = client.get(url)
    assert response.status_code == 404
    assert response.json() == {"detail": "Not found."}


@pytest.mark.django_db
def test_filter_tags_posts_empty(client: Client) -> None:
    url = reverse("api-posts-list") + "?tags=foo,bar/"
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        "count": 0,
        "next": None,
        "previous": None,
        "results": [],
    }


@pytest.mark.django_db
def test_list_posts_single(client: Client, dummy_post: Post) -> None:
    url = reverse("api-posts-list")
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": dummy_post.id,
                "title": dummy_post.title,
                "published": serializers.DateTimeField().to_representation(
                    dummy_post.published
                ),
                "tags": [tag.name for tag in dummy_post.tags.all()],
                "image": dummy_post.image.name,
            }
        ],
    }


@pytest.mark.django_db
def test_filter_tags_posts_single(
    client: Client, dozen_dummy_posts: List[Post]
) -> None:
    url = reverse("api-posts-list") + "?tags=tag0,tag1,tag2"
    response = client.get(url)
    assert response.status_code == 200
    assert response.json() == {
        "count": 3,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": post.id,
                "title": post.title,
                "published": serializers.DateTimeField().to_representation(
                    post.published
                ),
                "tags": [tag.name for tag in post.tags.all()],
                "image": post.image.name,
            }
            for post in reversed(dozen_dummy_posts[:3])
        ],
    }
