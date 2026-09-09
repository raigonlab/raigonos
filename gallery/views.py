from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ArtworkForm, CollectionForm
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


@login_required
def dashboard(request):
    collections = request.user.collections.all()
    return render(request, 'gallery/dashboard.html', {'collections': collections})


@login_required
def collection_create(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.owner = request.user
            collection.save()
            return redirect('gallery:dashboard')
    else:
        form = CollectionForm()
    return render(request, 'gallery/collection_form.html', {'form': form})


@login_required
def collection_update(request, slug):
    collection = get_object_or_404(Collection, slug=slug, owner=request.user)
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES, instance=collection)
        if form.is_valid():
            form.save()
            return redirect('gallery:dashboard')
    else:
        form = CollectionForm(instance=collection)
    return render(
        request,
        'gallery/collection_form.html',
        {'form': form, 'collection': collection},
    )


@login_required
def collection_delete(request, slug):
    collection = get_object_or_404(Collection, slug=slug, owner=request.user)
    if request.method == 'POST':
        collection.delete()
        return redirect('gallery:dashboard')
    return render(
        request, 'gallery/collection_confirm_delete.html', {'collection': collection}
    )


@login_required
def artwork_create(request, slug):
    collection = get_object_or_404(Collection, slug=slug, owner=request.user)
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.collection = collection
            artwork.save()
            return redirect('gallery:dashboard')
    else:
        form = ArtworkForm()
    return render(
        request,
        'gallery/artwork_form.html',
        {'form': form, 'collection': collection},
    )


@login_required
def artwork_update(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, collection__owner=request.user)
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES, instance=artwork)
        if form.is_valid():
            form.save()
            return redirect('gallery:dashboard')
    else:
        form = ArtworkForm(instance=artwork)
    return render(
        request,
        'gallery/artwork_form.html',
        {'form': form, 'collection': artwork.collection},
    )


@login_required
def artwork_delete(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, collection__owner=request.user)
    if request.method == 'POST':
        artwork.delete()
        return redirect('gallery:dashboard')
    return render(
        request, 'gallery/artwork_confirm_delete.html', {'artwork': artwork}
    )


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
