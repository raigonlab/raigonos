from django import forms

from .models import Artwork, Collection


class ImagePreviewInput(forms.ClearableFileInput):
    """File input that shows the current image as a thumbnail, instead of
    Django's default "Currently: <path>" text."""

    template_name = 'gallery/widgets/image_preview_input.html'


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['title', 'description', 'cover_image', 'status']
        widgets = {'cover_image': ImagePreviewInput}


class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['title', 'image', 'medium', 'year', 'description', 'display_order']
        widgets = {'image': ImagePreviewInput}
