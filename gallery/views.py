from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, Max, Min
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ArtworkForm, CollectionForm
from .models import Artwork, Collection


def artwork_gallery(request):
    artworks = Artwork.objects.filter(
        collection__status=Collection.STATUS_PUBLISHED
    ).select_related('collection')
    exhibition = [
        {
            'title': artwork.title,
            'src': artwork.image.url,
            'url': reverse('gallery:artwork_detail', args=[artwork.pk]),
        }
        for artwork in artworks
    ]
    return render(
        request,
        'gallery/artwork_gallery.html',
        {
            'artworks': artworks,
            'exhibition': exhibition,
            'artist_name': settings.ARTIST_NAME,
        },
    )


def collection_list(request):
    collections = Collection.objects.filter(
        status=Collection.STATUS_PUBLISHED
    ).annotate(
        artwork_count=Count('artworks'),
        first_year=Min('artworks__year'),
        last_year=Max('artworks__year'),
    )
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
    query = request.GET.get('q', '').strip()
    collections = request.user.collections.exclude(status=Collection.STATUS_ARCHIVED)
    if query:
        collections = collections.filter(title__icontains=query)
    return render(
        request,
        'gallery/dashboard.html',
        {'collections': collections, 'query': query},
    )


@login_required
def collection_archive_list(request):
    query = request.GET.get('q', '').strip()
    collections = request.user.collections.filter(status=Collection.STATUS_ARCHIVED)
    if query:
        collections = collections.filter(title__icontains=query)
    return render(
        request,
        'gallery/collection_archive_list.html',
        {'collections': collections, 'query': query, 'active_nav': 'archive'},
    )


@login_required
def artwork_list(request):
    query = request.GET.get('q', '').strip()
    artworks = Artwork.objects.filter(collection__owner=request.user).select_related(
        'collection'
    )
    if query:
        artworks = artworks.filter(title__icontains=query)
    return render(
        request,
        'gallery/artwork_list.html',
        {'artworks': artworks, 'active_nav': 'artworks', 'query': query},
    )


@login_required
def artwork_manage(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, collection__owner=request.user)
    siblings = list(artwork.collection.artworks.all())
    index = siblings.index(artwork)
    previous_artwork = siblings[index - 1] if index > 0 else None
    next_artwork = siblings[index + 1] if index < len(siblings) - 1 else None
    return render(
        request,
        'gallery/artwork_manage.html',
        {
            'artwork': artwork,
            'previous_artwork': previous_artwork,
            'next_artwork': next_artwork,
            'active_nav': 'collections',
        },
    )


@login_required
def collection_manage(request, slug):
    collection = get_object_or_404(Collection, slug=slug, owner=request.user)
    query = request.GET.get('q', '').strip()
    artworks = collection.artworks.all()
    if query:
        artworks = artworks.filter(title__icontains=query)
    nav = 'archive' if collection.status == Collection.STATUS_ARCHIVED else 'collections'
    return render(
        request,
        'gallery/collection_manage.html',
        {
            'collection': collection,
            'artworks': artworks,
            'query': query,
            'active_nav': nav,
        },
    )


@login_required
def collection_archive(request, slug):
    collection = get_object_or_404(Collection, slug=slug, owner=request.user)
    if request.method == 'POST':
        collection.status = Collection.STATUS_ARCHIVED
        collection.save()
        messages.success(request, f'Collection "{collection.title}" archived.')
        return redirect('gallery:dashboard')
    return redirect('gallery:collection_manage', slug=collection.slug)


@login_required
def collection_unarchive(request, slug):
    collection = get_object_or_404(Collection, slug=slug, owner=request.user)
    if request.method == 'POST':
        collection.status = Collection.STATUS_DRAFT
        collection.save()
        messages.success(
            request, f'Collection "{collection.title}" restored to Draft.'
        )
        return redirect('gallery:collection_manage', slug=collection.slug)
    return redirect('gallery:collection_archive_list')


@login_required
def collection_create(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.owner = request.user
            collection.save()
            messages.success(request, f'Collection "{collection.title}" created.')
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
            messages.success(request, f'Collection "{collection.title}" updated.')
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
        title = collection.title
        collection.delete()
        messages.success(request, f'Collection "{title}" deleted.')
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
            messages.success(request, f'Artwork "{artwork.title}" added.')
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
            messages.success(request, f'Artwork "{artwork.title}" updated.')
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
        title = artwork.title
        artwork.delete()
        messages.success(request, f'Artwork "{title}" deleted.')
        return redirect('gallery:dashboard')
    return render(
        request, 'gallery/artwork_confirm_delete.html', {'artwork': artwork}
    )


def _selected_ids(request):
    return [i for i in request.POST.getlist('ids') if i.isdigit()]


def _safe_next(request):
    """The page a bulk action started from, only if it is on this site."""
    target = request.POST.get('next', '')
    if url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return target
    return ''


def _redirect_back(request):
    return redirect(_safe_next(request) or 'gallery:dashboard')


BULK_COLLECTION_STATUS = {
    'draft': (Collection.STATUS_DRAFT, 'moved to Draft'),
    'publish': (Collection.STATUS_PUBLISHED, 'published'),
    'archive': (Collection.STATUS_ARCHIVED, 'archived'),
}


@login_required
@require_POST
def collection_bulk_action(request):
    collections = request.user.collections.filter(pk__in=_selected_ids(request))
    action = request.POST.get('action')
    count = collections.count()
    if not count:
        messages.info(request, 'Nothing was selected.')
        return _redirect_back(request)

    if action in BULK_COLLECTION_STATUS:
        status, verb = BULK_COLLECTION_STATUS[action]
        collections.update(status=status)
        messages.success(
            request, f'{count} Collection{"s" if count != 1 else ""} {verb}.'
        )
        return _redirect_back(request)

    if action == 'delete':
        if request.POST.get('confirm'):
            artwork_count = Artwork.objects.filter(collection__in=collections).count()
            collections.delete()
            messages.success(
                request,
                f'{count} Collection{"s" if count != 1 else ""} deleted '
                f'(with {artwork_count} artwork{"s" if artwork_count != 1 else ""}).',
            )
            return _redirect_back(request)
        return render(
            request,
            'gallery/bulk_confirm_delete.html',
            {
                'kind': 'Collection',
                'items': collections,
                'artwork_count': Artwork.objects.filter(
                    collection__in=collections
                ).count(),
                'form_action': request.path,
                'next': _safe_next(request),
            },
        )

    messages.error(request, 'Unknown action.')
    return _redirect_back(request)


@login_required
@require_POST
def artwork_bulk_delete(request):
    artworks = Artwork.objects.filter(
        pk__in=_selected_ids(request), collection__owner=request.user
    )
    count = artworks.count()
    if not count:
        messages.info(request, 'Nothing was selected.')
        return _redirect_back(request)

    if request.POST.get('confirm'):
        artworks.delete()
        messages.success(
            request, f'{count} Artwork{"s" if count != 1 else ""} deleted.'
        )
        return _redirect_back(request)

    return render(
        request,
        'gallery/bulk_confirm_delete.html',
        {
            'kind': 'Artwork',
            'items': artworks,
            'form_action': request.path,
            'next': _safe_next(request),
        },
    )


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('gallery:artwork_gallery')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account is ready.')
            return redirect('gallery:artwork_gallery')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})
