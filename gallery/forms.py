from django import forms

from .models import Artwork, Collection


class ImagePreviewInput(forms.ClearableFileInput):
    """File input that shows the current image as a thumbnail, instead of
    Django's default "Currently: <path>" text."""

    # Points at a custom widget template instead of Django's built-in
    # one, so the owner can actually see the image they're about to
    # replace on the Edit forms.
    template_name = 'gallery/widgets/image_preview_input.html'


# Plain ModelForms for the two models — Django builds the fields and
# validation straight from the model definition, so there's no need to
# repeat field types/validation here. Only the widget for the image
# fields is overridden, to use the thumbnail preview above.

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
