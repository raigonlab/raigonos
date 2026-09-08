from django.contrib import admin

from .models import Artwork, Collection


class ArtworkInline(admin.TabularInline):
    model = Artwork
    extra = 1
    fields = ('title', 'image', 'medium', 'year', 'display_order')


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
