from django.urls import path

from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.collection_list, name='collection_list'),
    path(
        'collection/<slug:slug>/',
        views.collection_detail,
        name='collection_detail',
    ),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path(
        'dashboard/collections/new/',
        views.collection_create,
        name='collection_create',
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
