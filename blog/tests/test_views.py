from __future__ import annotations

import typing

import pytest
from django.urls import reverse

if typing.TYPE_CHECKING:
    from typing import List

    from django.test import Client

    from blog.models import Post


@pytest.mark.django_db
def test_index_no_posts(client: Client) -> None:
    response = client.get(reverse("posts"))
    assert response.status_code == 200
    assert b"No posts yet" in response.content


@pytest.mark.usefixtures("dozen_dummy_posts")
@pytest.mark.django_db
def test_no_posts_filter_by_tags(client: Client) -> None:
    response = client.get(reverse("posts") + "?tags=foo,bar")
    assert response.status_code == 200
    assert b"No posts yet" in response.content


@pytest.mark.django_db
def test_index_single_post(client: Client, dummy_post: Post) -> None:
    response = client.get(reverse("posts"))
    assert response.status_code == 200
    content = response.content.decode()
    assert dummy_post.title in content
    assert dummy_post.preview() in content
    for tag in dummy_post.tags.all():
        assert tag.name in content


@pytest.mark.django_db
def test_filter_posts_by_tags(client: Client, dozen_dummy_posts: List[Post]) -> None:
    tags = ",".join(
        tag.name for post in dozen_dummy_posts[:3] for tag in post.tags.all()
    )
    response = client.get(reverse("posts") + f"?tags={tags}")
    content = response.content.decode()
    assert response.status_code == 200
    for post in dozen_dummy_posts[:3]:
        assert post.title in content
        assert reverse("post-detail", args=(post.id,)) in content


@pytest.mark.usefixtures("dozen_dummy_posts")
@pytest.mark.django_db
def test_index_pagination(client: Client) -> None:
    response = client.get(reverse("posts"))
    content = response.content.decode()
    assert response.status_code == 200
    assert "pagination" in content
    assert "Previous" in content
    assert "Next" in content


@pytest.mark.django_db
def test_post_detail(client: Client, dummy_post: Post) -> None:
    response = client.get(reverse("post-detail", args=(dummy_post.id,)))
    content = response.content.decode()
    assert response.status_code == 200
    assert dummy_post.title in content
    assert dummy_post.content in content
    for tag in dummy_post.tags.all():
        assert tag.name in content
