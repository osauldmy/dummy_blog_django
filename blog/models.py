from __future__ import annotations

from django.db import models
from taggit.managers import TaggableManager


class Post(models.Model):
    title = models.CharField(max_length=128)
    content = models.TextField()
    tags = TaggableManager(blank=True)
    image = models.ImageField(upload_to="blog", blank=True, null=True)
    published = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def preview(self) -> str:
        if len(self.content) > 512:
            return self.content[:512] + " ..."
        return self.content

    def __str__(self) -> str:
        return str(self.title)
