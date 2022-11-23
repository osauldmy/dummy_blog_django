from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.routers import DefaultRouter

from blog import api, views

schema_view = get_schema_view(  # pylint: disable=invalid-name
    openapi.Info(
        title="Blog API",
        default_version="v1",
        description="Few read-only public views for browsing blog posts",
    ),
    public=True,
)

router = DefaultRouter()
router.register("posts", api.PostViewSet, basename="api-posts")

urlpatterns = [
    path("api/", schema_view.with_ui("swagger", cache_timeout=0)),
    path("api.json", schema_view.without_ui(cache_timeout=0)),
    path("api.yaml", schema_view.without_ui(cache_timeout=0)),
    path("api/", include(router.urls)),
    path("posts", views.index, name="posts"),
    path("posts/<int:post_id>/", views.post_detail, name="post-detail"),
]
