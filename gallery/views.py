from django.shortcuts import get_object_or_404, render

from .models import Artwork, Collection


def collection_list(request):
    collections = Collection.objects.filter(status=Collection.STATUS_PUBLISHED)
    return render(
        request, 'gallery/collection_list.html', {'collections': collections}
    )


def collection_detail(request, slug):
    collection = get_object_or_404(
        Collection, slug=slug, status=Collection.STATUS_PUBLISHED
    )
    return render(
        request, 'gallery/collection_detail.html', {'collection': collection}
    )


def artwork_detail(request, pk):
    artwork = get_object_or_404(
        Artwork, pk=pk, collection__status=Collection.STATUS_PUBLISHED
    )
    return render(request, 'gallery/artwork_detail.html', {'artwork': artwork})
