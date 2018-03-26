from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf.urls import url
from .models import Place
from .forms import NewPlaceForm, TripReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import photo_manager
import copy


@login_required
def place_list(request):

    # If a POST request, this must be from user clicking Add button
    # in the form. Check if new place is valid and add to list, then
    # redirect to 'place_list' route - which ends up creating a GET
    # request for this same method.
    if request.method == 'POST':
        form = NewPlaceForm(request.POST)
        place = form.save(commit=False)
        place.user = request.user
        if form.is_valid():
            place.save()
            return redirect('place_list')

    # If not a POST request, or the form is not valid, display the page
    # with the form, and place list
    places = Place.objects.filter(visited=False)
    form = NewPlaceForm()
    return render(request, 'travel_wishlist/wishlist.html', {'places' : places, 'form' : form})


@login_required
def places_visited(request):
    visited = Place.objects.filter(user=request.user, visited=True)
    return render(request, 'travel_wishlist/visited.html', {'visited':visited})


@login_required
def place_is_visited(request):
    if request.method == 'POST':
        place_pk = request.POST['place_pk']
        place = get_object_or_404(Place, pk=place_pk)
        place.visited = True
        place.save()

    return redirect('place_list')


@login_required
def delete_place(request):
    pk = request.POST['place_pk']
    place = get_object_or_404(Place, pk=pk)
    place.delete()
    return redirect('place_list')


@login_required
def place_details(request, place_pk):

    place = get_object_or_404(Place, pk=place_pk)

    if request.method == 'POST':

        # get a copy of the object so have a reference to the old photo,
        # just in case it needs to be deleted; user saves new photo or clears old one.
        old_place = get_object_or_404(Place, pk=place_pk)

        form = TripReviewForm(request.POST, request.FILES, instance=place)  # instance = model object to update with the form data
        if form.is_valid():

            # If there was a photo added or removed, delete any old photo
            if 'photo' in form.changed_data:
                photo_manager.delete_photo(old_place.photo)

            form.save()

            messages.info(request, 'Trip information updated!')

        else:
            messages.error(request, form.errors)  # This looks hacky, replace

        return redirect('place_details', place_pk=place_pk)


    else:    # GET place details

        if place.visited:
            review_form = TripReviewForm(instance=place)  # Pre-populate with data from this Place instance
            return render(request, 'travel_wishlist/place_detail.html', {'place':place, 'review_form':review_form } )

        else:

            return render(request, 'travel_wishlist/place_detail.html', {'place':place} )
