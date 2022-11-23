from __future__ import annotations

import typing

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from taggit.forms import TagField, TagWidget

from blog.models import Post

if typing.TYPE_CHECKING:
    from typing import Any, Dict, Iterator, List, Optional, Sequence, Type

    from django.contrib.admin.views.main import ChangeList
    from django.db.models.query import QuerySet
    from django.http import HttpRequest


# NOTE: Modified for my use-case answer from
# https://stackoverflow.com/questions/39790087/is-multi-choice-django-admin-filters-possible
class MultiSelectTagsFilter(admin.FieldListFilter):
    def __init__(  # pylint: disable=too-many-arguments
        self,
        field: Any,
        request: HttpRequest,
        params: Dict[str, Any],
        model: Type[Post],
        model_admin: PostAdmin,
        field_path: str,
    ) -> None:
        self.lookup_kwarg = f"{field_path}__name__in"
        super().__init__(field, request, params, model, model_admin, field_path)
        self.lookup_val = set(self.used_parameters.get(self.lookup_kwarg, []))
        self.lookup_choices = model.tags.values_list("name", flat=True).distinct()

    def expected_parameters(self) -> List[str]:
        return [self.lookup_kwarg]

    def choices(self, changelist: ChangeList) -> Iterator[Dict[str, Any]]:
        for value in self.lookup_choices:
            values = self.lookup_val ^ {value}
            qs = (
                changelist.get_query_string(
                    {self.lookup_kwarg: ",".join(values)},
                )
                if values
                else changelist.get_query_string(remove=[self.lookup_kwarg])
            )
            yield {
                "display": f"#{value}",
                "selected": value in self.lookup_val,
                "query_string": qs,
            }


# FIXME: somehow PostAdmin.formfield_overrides doesn't work for this widget
TagField.widget = TagWidget(attrs={"size": "90"})


@admin.register(Post)
class PostAdmin(admin.ModelAdmin[Post]):  # pylint: disable=unsubscriptable-object
    list_display = (
        "title",
        "thumbnail",
        "preview",
        "tags_list",
        "public_url",
        "published",
        "last_modified",
    )
    readonly_fields = ("public_url", "published", "last_modified")
    list_filter = [("tags", MultiSelectTagsFilter)]

    def get_fields(self, _: HttpRequest, obj: Optional[Post] = None) -> Sequence[str]:
        fields = ["title", "content", "image", "tags"]
        if obj:
            fields.extend(["public_url", "last_modified", "published"])
        return fields

    def get_queryset(self, request: HttpRequest) -> QuerySet[Post]:
        # recommendation from django-taggit
        # https://django-taggit.readthedocs.io/en/latest/admin.html
        return super().get_queryset(request).prefetch_related("tags")

    def lookup_allowed(self, lookup: str, value: str) -> bool:
        if lookup == "tags__name__in":
            return True
        return super().lookup_allowed(lookup, value)

    def thumbnail(self, obj: Post) -> Optional[str]:
        # NOTE: didn't do thumbnail creation on file saving, could be added.
        # Instead just showing smaller version of real file when needed.
        return format_html(
            '<img src="{}" width="75" height="75"/>',
            obj.image.url if obj.image else "/static/default.png",
        )

    @admin.display(description="tags")
    def tags_list(self, obj: Post) -> str:
        return "\n".join(f"#{tag.name}" for tag in obj.tags.all())

    def public_url(self, obj: Post) -> str:
        url = reverse("post-detail", args=(obj.id,))
        return format_html("<a href='{}'>click!</a>", url)
