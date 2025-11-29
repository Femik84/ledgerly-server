from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def generate_unique_slug(model_cls, value, instance=None):
    """Generate a unique slug for `model_cls` based on `value`.

    If the generated slug already exists, append `-1`, `-2`, ... until unique.
    If `instance` is provided it will be excluded from the uniqueness check
    (useful when updating an existing object).
    """
    base_slug = slugify(value)
    slug = base_slug
    i = 1
    while True:
        qs = model_cls.objects.filter(slug=slug)
        if instance is not None:
            qs = qs.exclude(pk=instance.pk)
        if not qs.exists():
            return slug
        slug = f"{base_slug}-{i}"
        i += 1


class Category(models.Model):
    """Category model with auto unique slug."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate or normalize slug if missing or changed
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.name, instance=self)
        else:
            normalized = slugify(self.slug)
            if normalized != self.slug or (
                Category.objects.filter(slug=normalized).exclude(pk=self.pk).exists()
            ):
                self.slug = generate_unique_slug(Category, normalized, instance=self)
        super().save(*args, **kwargs)
