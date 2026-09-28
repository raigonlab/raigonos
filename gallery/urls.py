from django.urls import path

from . import views

app_name = 'gallery'

urlpatterns = [
    # Public pages — no login needed, only ever show published Collections.
    path('', views.artwork_gallery, name='artwork_gallery'),
    path('collections/', views.collection_list, name='collection_list'),
    path(
        'collection/<slug:slug>/',
        views.collection_detail,
        name='collection_detail',
    ),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),

    # Dashboard — everything below here is behind @login_required in
    # views.py and scoped to the logged-in owner's own Collections/Artworks.
    path('dashboard/', views.dashboard, name='dashboard'),
    path(
        'dashboard/archive/',
        views.collection_archive_list,
        name='collection_archive_list',
    ),
    path('dashboard/artworks/', views.artwork_list, name='artwork_list'),
    path(
        'dashboard/artworks/<int:pk>/',
        views.artwork_manage,
        name='artwork_manage',
    ),

    # Bulk actions (Select mode) — POST-only endpoints for acting on
    # several Collections/Artworks at once.
    path(
        'dashboard/collections/bulk/',
        views.collection_bulk_action,
        name='collection_bulk_action',
    ),
    path(
        'dashboard/artworks/bulk-delete/',
        views.artwork_bulk_delete,
        name='artwork_bulk_delete',
    ),

    # Collection CRUD.
    path(
        'dashboard/collections/new/',
        views.collection_create,
        name='collection_create',
    ),
    path(
        'dashboard/collections/<slug:slug>/',
        views.collection_manage,
        name='collection_manage',
    ),
    path(
        'dashboard/collections/<slug:slug>/edit/',
        views.collection_update,
        name='collection_update',
    ),
    path(
        'dashboard/collections/<slug:slug>/delete/',
        views.collection_delete,
        name='collection_delete',
    ),
    path(
        'dashboard/collections/<slug:slug>/archive/',
        views.collection_archive,
        name='collection_archive',
    ),
    path(
        'dashboard/collections/<slug:slug>/unarchive/',
        views.collection_unarchive,
        name='collection_unarchive',
    ),

    # Artwork CRUD — creation is nested under its Collection's slug;
    # edit/delete only need the Artwork's own id.
    path(
        'dashboard/collections/<slug:slug>/artworks/new/',
        views.artwork_create,
        name='artwork_create',
    ),
    path(
        'dashboard/artworks/<int:pk>/edit/',
        views.artwork_update,
        name='artwork_update',
    ),
    path(
        'dashboard/artworks/<int:pk>/delete/',
        views.artwork_delete,
        name='artwork_delete',
    ),
]
