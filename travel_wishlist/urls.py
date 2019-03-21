from django.urls import path
from . import views

urlpatterns = [
    path(r'', views.place_list, name='place_list'),
    path(r'visited', views.places_visited, name='places_visited'),
    path(r'was_visited', views.place_was_visited, name='place_was_visited'),
    path(r'place/<int:place_pk>', views.place_details, name='place_details'),
    path(r'delete', views.delete_place, name='delete_place'),
]
