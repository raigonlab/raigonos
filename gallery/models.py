from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class Collection(models.Model):
    """A themed group of Artworks belonging to one owner (artist)."""

    # A Collection is always in one of these three states. Draft and
    # Archived are only ever shown to the owner in the dashboard; only
    # Published Collections (and their Artworks) are visible on the
    # public site.
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft (only visible to you)'),
        (STATUS_PUBLISHED, 'Published (visible in the public gallery)'),
        (STATUS_ARCHIVED, 'Archived (kept on record, never public)'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collections',
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(
        upload_to='collections/covers/', blank=True, null=True
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # The slug only needs generating once, when the Collection is
        # first created — after that it stays fixed even if the title
        # changes later, so existing public URLs keep working.
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        # Turn the title into a URL-safe slug (e.g. "My Art" -> "my-art").
        # If that slug is already taken by another Collection, keep
        # appending a number until it's unique, since slug has to be
        # unique for the public collection/<slug>/ URL to work.
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while Collection.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            counter += 1
            slug = f'{base_slug}-{counter}'
        return slug


class Artwork(models.Model):
    """A single piece of art belonging to a Collection."""

    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name='artworks'
    )
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='artworks/')
    medium = models.CharField(
        max_length=100, blank=True, help_text='e.g. Digital painting, Oil on canvas'
    )
    # Range check: rules out nonsense values (0, 99999) while staying
    # wide enough to never need revisiting for a living artist's work.
    year = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1000), MaxValueValidator(2100)],
    )
    description = models.TextField(blank=True)
    # Lets the owner control the order Artworks appear in within a
    # Collection, instead of being stuck with creation order.
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title
