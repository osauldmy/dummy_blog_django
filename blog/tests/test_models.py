from __future__ import annotations

import typing

import pytest

from blog.models import Post

if typing.TYPE_CHECKING:
    from typing import List


@pytest.mark.django_db
def test_tags_filter(dozen_dummy_posts: List[Post]) -> None:
    tag = "tag3"
    fourth = dozen_dummy_posts[3]
    assert Post.objects.get(tags__name=tag) == fourth
