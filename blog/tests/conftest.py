from __future__ import annotations

import typing

import pytest
from django.utils import lorem_ipsum

from blog.models import Post

if typing.TYPE_CHECKING:
    from typing import List


@pytest.fixture(scope="function")
def dummy_post() -> Post:
    post = Post.objects.create(title="Dummy", content="Dummy content")
    post.tags.add("foo", "bar")
    return post


@pytest.fixture(scope="function")
def dozen_dummy_posts() -> List[Post]:
    posts = Post.objects.bulk_create(
        (
            Post(
                title=f"Post {i}",
                content="\n".join(lorem_ipsum.paragraphs(i)),
            )
            for i in range(10)
        )
    )

    for index, post in enumerate(posts):
        post.tags.add(f"tag{index}")
    return posts
