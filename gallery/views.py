from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

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


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('gallery:collection_list')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('gallery:collection_list')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})
