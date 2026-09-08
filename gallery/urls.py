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
]
