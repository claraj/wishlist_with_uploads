from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf.urls import url
from .models import Place
from .forms import NewPlaceForm, TripReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def place_list(request):

    """ If this is a POST request, the user clicked the Add button
    in the form. Check if the new place is valid, if so, save a
    new Place to the database, and redirect to this same page.
    This creates a GET request to this same route.

    If not a POST route, or Place is not valid, display a page with
    a list of places and a form to add a new place.
    """

    if request.method == 'POST':
        form = NewPlaceForm(request.POST)
        place = form.save(commit=False)
        place.user = request.user  # associate the place with the current logged-in user 
        if form.is_valid():
            place.save()
            return redirect('place_list')

    # If not a POST request, or the form is not valid, display the page
    # with the form, and place list
    places = Place.objects.filter(visited=False).order_by('name')
    form = NewPlaceForm()
    return render(request, 'travel_wishlist/wishlist.html', {'places': places, 'new_place_form': form})


@login_required
def places_visited(request):
    visited = Place.objects.filter(user=request.user, visited=True)
    return render(request, 'travel_wishlist/visited.html', {'visited': visited})


@login_required
def place_was_visited(request):
    if request.method == 'POST':
        place_pk = request.POST.get('pk')
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
        form = TripReviewForm(request.POST, request.FILES, instance=place)  # instance = model object to update with the form data
        if form.is_valid():
            form.save()
            messages.info(request, 'Trip information updated!')
        else:
            messages.error(request, form.errors)  # This looks hacky, replace

        return redirect('place_details', place_pk=place_pk)

    else:    # GET place details
        if place.visited:
            review_form = TripReviewForm(instance=place)  # Pre-populate with data from this Place instance
            return render(request, 'travel_wishlist/place_detail.html', {'place': place, 'review_form': review_form} )

        else:
            return render(request, 'travel_wishlist/place_detail.html', {'place': place} )
