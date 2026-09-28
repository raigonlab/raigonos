from django.contrib import admin

from .models import Artwork, Collection


# Lets an Artwork be added/edited directly on its Collection's admin
# page, instead of needing to jump to a separate Artwork admin page.
class ArtworkInline(admin.TabularInline):
    model = Artwork
    extra = 1
    fields = ('title', 'image', 'medium', 'year', 'display_order')


# Admin registration is only used for site maintenance/debugging by the
# developer — regular owners manage their Collections and Artworks
# through the dashboard views, not this admin site.
@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ArtworkInline]


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'collection', 'medium', 'year', 'display_order')
    list_filter = ('collection',)
    search_fields = ('title', 'description')
