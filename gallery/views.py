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


# -----------------------------------------------------------------------
# Public views — no login required. Every query here filters on
# status=STATUS_PUBLISHED (or a Collection's status, for Artworks), so a
# visitor can never see a draft or archived Collection, even by guessing
# its URL.
# -----------------------------------------------------------------------

def artwork_gallery(request):
    # The public home page: every published Artwork, across every
    # Collection. `exhibition` is a small, JSON-friendly list built just
    # for the drifting-artwork animation in exhibition.js; the full
    # `artworks` queryset is passed too, for the no-JS plain grid.
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
    # Browsing by Collection instead of a flat feed. The annotations
    # compute the artwork count and year range in the database (one
    # query) rather than looping over each Collection's Artworks in
    # Python, so the page stays fast as the gallery grows.
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
    # get_object_or_404 with status=STATUS_PUBLISHED means a direct link
    # to a draft/archived Collection 404s, instead of leaking its content.
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
    # Work out this Artwork's Previous/Next neighbours within its own
    # Collection, so the detail page can let a visitor step through the
    # whole Collection without going back to the list each time.
    siblings = list(artwork.collection.artworks.all())
    index = siblings.index(artwork)
    return render(
        request,
        'gallery/artwork_detail.html',
        {
            'artwork': artwork,
            'previous_artwork': siblings[index - 1] if index > 0 else None,
            'next_artwork': (
                siblings[index + 1] if index < len(siblings) - 1 else None
            ),
            'position': index + 1,
            'total': len(siblings),
        },
    )


# -----------------------------------------------------------------------
# Dashboard views — everything below requires login, and every query is
# scoped to request.user (directly, or via collection__owner=request.user
# for Artworks). This is what stops one owner from ever seeing or
# touching another owner's Collections/Artworks.
# -----------------------------------------------------------------------

@login_required
def dashboard(request):
    # The owner's main "My Collections" list: Draft + Published, but not
    # Archived (archived ones have their own separate page below).
    query = request.GET.get('q', '').strip()
    collections = request.user.collections.exclude(
        status=Collection.STATUS_ARCHIVED
    )
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
    collections = request.user.collections.filter(
        status=Collection.STATUS_ARCHIVED
    )
    if query:
        collections = collections.filter(title__icontains=query)
    return render(
        request,
        'gallery/collection_archive_list.html',
        {'collections': collections, 'query': query, 'active_nav': 'archive'},
    )


@login_required
def artwork_list(request):
    # "All Artworks" flattens every Artwork the owner has, across all of
    # their Collections, into one list/grid.
    query = request.GET.get('q', '').strip()
    artworks = Artwork.objects.filter(
        collection__owner=request.user
    ).select_related('collection')
    if query:
        artworks = artworks.filter(title__icontains=query)
    return render(
        request,
        'gallery/artwork_list.html',
        {'artworks': artworks, 'active_nav': 'artworks', 'query': query},
    )


@login_required
def artwork_manage(request, pk):
    # Full-page preview of one Artwork, with Previous/Next through the
    # rest of its Collection — same idea as the public artwork_detail
    # view above, just scoped to the owner instead of published-only.
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
    # One Collection's own dashboard page: its Artworks, plus title
    # search scoped to just this Collection.
    collection = get_object_or_404(Collection, slug=slug, owner=request.user)
    query = request.GET.get('q', '').strip()
    artworks = collection.artworks.all()
    if query:
        artworks = artworks.filter(title__icontains=query)
    is_archived = collection.status == Collection.STATUS_ARCHIVED
    nav = 'archive' if is_archived else 'collections'
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
    # Archiving/unarchiving only happens on POST, same pattern as delete
    # views: a GET just bounces back to where the action button lives,
    # rather than performing the change from a plain link.
    collection = get_object_or_404(Collection, slug=slug, owner=request.user)
    if request.method == 'POST':
        collection.status = Collection.STATUS_ARCHIVED
        collection.save()
        messages.success(request, f'Collection "{collection.title}" archived.')
        return redirect('gallery:dashboard')
    return redirect('gallery:collection_manage', slug=collection.slug)


@login_required
def collection_unarchive(request, slug):
    # Restoring always goes back to Draft, never straight to Published —
    # so nothing becomes public again without the owner deliberately
    # re-publishing it.
    collection = get_object_or_404(Collection, slug=slug, owner=request.user)
    if request.method == 'POST':
        collection.status = Collection.STATUS_DRAFT
        collection.save()
        messages.success(
            request, f'Collection "{collection.title}" restored to Draft.'
        )
        return redirect('gallery:collection_manage', slug=collection.slug)
    return redirect('gallery:collection_archive_list')


# -----------------------------------------------------------------------
# Collection CRUD. Same shape for all three: GET shows a form (blank for
# create, pre-filled for update), POST validates and saves it. Delete
# follows the project's confirm-page convention — GET renders a
# confirmation template, only POST actually deletes anything.
# -----------------------------------------------------------------------

@login_required
def collection_create(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST, request.FILES)
        if form.is_valid():
            # commit=False so the owner can be set before the row is
            # actually written — the form itself never lets the user
            # pick their own owner field, so it has to be set here.
            collection = form.save(commit=False)
            collection.owner = request.user
            collection.save()
            messages.success(
                request, f'Collection "{collection.title}" created.'
            )
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
            messages.success(
                request, f'Collection "{collection.title}" updated.'
            )
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
        request,
        'gallery/collection_confirm_delete.html',
        {'collection': collection},
    )


# -----------------------------------------------------------------------
# Artwork CRUD — same shape as Collection CRUD above, just nested under
# a Collection for creation.
# -----------------------------------------------------------------------

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


# -----------------------------------------------------------------------
# Bulk actions — support for the dashboard's "Select" mode, where the
# owner can tick several Collections/Artworks at once and apply one
# action to all of them (Draft/Publish/Archive/Delete). Both views below
# are POST-only and re-filter on request.user, so even a crafted request
# with someone else's ids can only ever touch the logged-in owner's own
# rows.
# -----------------------------------------------------------------------

def _selected_ids(request):
    # Only keep values that actually look like a database id, so a
    # malformed "ids" field can't reach the queryset filters below.
    return [i for i in request.POST.getlist('ids') if i.isdigit()]


def _safe_next(request):
    """The page a bulk action started from, only if it is on this site."""
    # Guards against an open redirect: without this check, a "next" value
    # pointing at an external site would send the owner there after the
    # action completes.
    target = request.POST.get('next', '')
    if url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}
    ):
        return target
    return ''


def _redirect_back(request):
    return redirect(_safe_next(request) or 'gallery:dashboard')


# Maps each bulk-action button to the Collection status it sets and the
# word used in the success message.
BULK_COLLECTION_STATUS = {
    'draft': (Collection.STATUS_DRAFT, 'moved to Draft'),
    'publish': (Collection.STATUS_PUBLISHED, 'published'),
    'archive': (Collection.STATUS_ARCHIVED, 'archived'),
}


@login_required
@require_POST
def collection_bulk_action(request):
    collections = request.user.collections.filter(
        pk__in=_selected_ids(request)
    )
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
        # Deleting still needs a second, explicit confirmation step
        # (the "confirm" field) rather than deleting on the first POST,
        # same as the single-item delete views' confirm-page pattern —
        # just server-rendered here instead of a separate page reload.
        if request.POST.get('confirm'):
            artwork_count = Artwork.objects.filter(
                collection__in=collections
            ).count()
            collections.delete()
            artwork_plural = 's' if artwork_count != 1 else ''
            messages.success(
                request,
                f'{count} Collection{"s" if count != 1 else ""} deleted '
                f'(with {artwork_count} artwork{artwork_plural}).',
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


# -----------------------------------------------------------------------
# Auth — signup only. Login/logout are handled entirely by Django's
# built-in auth views (see raigonos/urls.py), which is enough since
# nothing about them needs customising for this project.
# -----------------------------------------------------------------------

def signup_view(request):
    # Already-logged-in users don't need the signup form; send them
    # straight to the gallery instead of showing it again.
    if request.user.is_authenticated:
        return redirect('gallery:artwork_gallery')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the new user in immediately, so they land in an
            # authenticated session straight after signing up instead of
            # having to log in again with the password they just typed.
            login(request, user)
            messages.success(
                request, f'Welcome, {user.username}! Your account is ready.'
            )
            return redirect('gallery:artwork_gallery')
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})
