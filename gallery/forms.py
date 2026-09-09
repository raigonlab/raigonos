from django import forms

from .models import Artwork, Collection


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['title', 'description', 'cover_image', 'status']


class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['title', 'image', 'medium', 'year', 'description', 'display_order']
