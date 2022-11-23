from __future__ import annotations

import typing

import pytest
from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils.html import format_html

from blog.admin import PostAdmin
from blog.models import Post

if typing.TYPE_CHECKING:
    from django.test import Client


@pytest.mark.parametrize(
    "url",
    (
        reverse("admin:index"),
        reverse("admin:blog_post_changelist"),
        reverse("admin:blog_post_change", args=(1,)),
        reverse("admin:blog_post_delete", args=(1,)),
    ),
)
@pytest.mark.django_db
def test_admin_without_login(url: str, client: Client) -> None:
    response = client.get(url)
    assert response.status_code == 302
    assert response.headers["Location"] == f"/admin/login/?next={url}"


@pytest.mark.parametrize(
    "url, expected_status_code",
    (
        (reverse("admin:index"), 200),
        (reverse("admin:blog_post_changelist"), 200),
        (reverse("admin:blog_post_change", args=(1,)), 302),
        (reverse("admin:blog_post_delete", args=(1,)), 302),
    ),
)
@pytest.mark.django_db
def test_admin_with_login(
    url: str, expected_status_code: int, admin_client: Client
) -> None:
    assert admin_client.get(url).status_code == expected_status_code


@pytest.mark.django_db
def test_admin_with_one_post(
    admin_client: Client,
    dummy_post: Post,
) -> None:
    change_url = reverse("admin:blog_post_change", args=(dummy_post.id,))
    assert admin_client.get(change_url).status_code == 200

    dummy_post.delete()
    assert admin_client.get(change_url).status_code == 302


@pytest.mark.usefixtures("dozen_dummy_posts")
@pytest.mark.django_db
def test_admin_filter_by_tags(admin_client: Client) -> None:
    tags_url = reverse("admin:blog_post_changelist") + "?tags__name__in="
    assert b"0 posts" in admin_client.get(tags_url + "foo").content
    assert b"1 post" in admin_client.get(tags_url + "tag0").content
    assert b"2 posts" in admin_client.get(tags_url + "tag0,tag1").content


@pytest.mark.django_db
def test_admin_custom_list_display(dummy_post: Post) -> None:
    post_admin = PostAdmin(Post, AdminSite())

    assert post_admin.public_url(dummy_post) == format_html(
        "<a href='{}'>click!</a>", reverse("post-detail", args=(dummy_post.id,))
    )
    assert post_admin.tags_list(dummy_post) in ("#bar\n#foo", "#foo\n#bar")
    assert (
        post_admin.thumbnail(dummy_post)
        == '<img src="/static/default.png" width="75" height="75"/>'
    )
