from __future__ import annotations

import typing

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from blog.models import Post

if typing.TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

POSTS_PER_PAGE = 3


def index(request: HttpRequest) -> HttpResponse:
    tags = request.GET.get("tags", "")
    posts = (
        Post.objects.filter(tags__name__in=tags.split(",")).distinct()
        if tags
        else Post.objects.prefetch_related("tags").all()
    )
    paginator = Paginator(posts.order_by("-published"), POSTS_PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "index.html", {"page": page})


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)
    return render(request, "detail.html", {"post": post})
