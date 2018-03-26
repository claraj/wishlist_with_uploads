from django.test import TestCase
from django.urls import reverse

from .models import Place
from django.contrib.auth.models import User


class TestViewHomePageIsEmptyList(TestCase):

    fixtures = ['test_users']

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)

    def test_load_wishlist_page_shows_empty_list(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        self.assertEquals(0, len(response.context['places']))

    def test_load_visted_page_shows_empty_list(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertEquals(0, len(response.context['visited']))


class TestWishList(TestCase):

    # Load this data into the database for all of the tests in this class
    fixtures = ['test_places', 'test_users']

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)


    def test_view_wishlist(self):
        response = self.client.get(reverse('place_list'))
        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # What data was sent to the template?
        data_rendered = list(response.context['places'])
        # What data is in the database? Get all of the items where visited = False
        data_expected = list(Place.objects.filter(visited=False))
        # Is it the same?
        self.assertCountEqual(data_rendered, data_expected)


    def test_view_places_visited(self):
        response = self.client.get(reverse('places_visited'))
        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')

        # What data was sent to the template?
        data_rendered = list(response.context['visited'])
        # What data is in the database? Get all of the items where visited = false
        data_expected = list(Place.objects.filter(visited=True))
        # Is it the same?
        self.assertCountEqual(data_rendered, data_expected)


class TestAddNewPlace(TestCase):

    # Load this data into the database for all of the tests in this class
    fixtures = ['test_users']

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)

    def test_add_new_unvisited_place_to_wishlist(self):

        response = self.client.post(reverse('place_list'), { 'name': 'Tokyo', 'visited': False}, follow=True)

        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # What data was used to populate the template?
        response_places = response.context['places']
        # Should be 1 item
        self.assertEqual(len(response_places), 1)
        tokyo_response = response_places[0]

        # Expect this data to be in the database. Use get() to get data with
        # the values expected. Will throw an exception if no data, or more than
        # one row, matches. Remember throwing an exception will cause this test to fail
        tokyo_in_database = Place.objects.get(name="Tokyo", visited=False)

        # Is the data used to render the template, the same as the data in the database?
        self.assertEqual(tokyo_response, tokyo_in_database)

        # And add another place - still works?
        response =  self.client.post(reverse('place_list'), { 'name': 'Yosemite', 'visited': False}, follow=True)

        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # What data was used to populate the template?
        response_places = response.context['places']
        # Should be 2 items
        self.assertEqual(len(response_places), 2)

        # Expect this data to be in the database. Use get() to get data with
        # the values expected. Will throw an exception if no data, or more than
        # one row, matches. Remember throwing an exception will cause this test to fail
        place_in_database = Place.objects.get(name="Yosemite", visited=False)
        place_in_database = Place.objects.get(name="Tokyo", visited=False)

        places_in_database = Place.objects.all()  # Get all data

        # Is the data used to render the template, the same as the data in the database?
        self.assertCountEqual(list(places_in_database), list(response_places))


    def test_add_new_visited_place_to_wishlist(self):

        response =  self.client.post(reverse('place_list'), { 'name': 'Tokyo', 'visited': True }, follow=True)

        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # What data was used to populate the template?
        response_places = response.context['places']
        # Should be 0 items - have not added any un-visited places
        self.assertEqual(len(response_places), 0)

        # Expect this data to be in the database. Use get() to get data with
        # the values expected. Will throw an exception if no data, or more than
        # one row, matches. Remember throwing an exception will cause this test to fail
        place_in_database = Place.objects.get(name="Tokyo", visited=True)


class TestMarkPlaceAsVisited(TestCase):
    # Load this data into the database for all of the tests in this class
    fixtures = ['test_places', 'test_users']

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)


    def test_mark_unvisited_place_as_visited(self):


        response = self.client.post(reverse('place_is_visited'), {'place_pk': 2}, follow=True)


        # Assert redirected to place list
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # Check database for correct data
        place = Place.objects.get(pk=2)
        self.assertTrue(place.visited)


    def test_mark_non_existent_place_as_visited_returns_404(self):
        response = self.client.post(reverse('place_is_visited'), {'place_pk': 200}, follow=True)
        self.assertEqual(404, response.status_code)


class TestPlaceDetail(TestCase):
    # Load this data into the database for all of the tests in this class
    fixtures = ['test_places', 'test_users']

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)


    def test_place_detail(self):

        place_1 = Place.objects.get(pk=1)

        response = self.client.get(reverse('place_details', kwargs={'place_pk':1} ))
        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/place_detail.html')

        # What data was sent to the template?
        data_rendered = response.context['place']

        # Same as data sent to template?
        self.assertEqual(data_rendered, place_1)

        # and correct data shown on page?
        text_rendered = str(response.content)
        assert 'Tokyo' in text_rendered
        assert 'cool' in text_rendered
        assert '2014-01-01' in text_rendered

        # TODO how to test correct image is shown?


    def test_modify_notes(self):

        response = self.client.post(reverse('place_details', kwargs={'place_pk':1}), {'notes':'awesome'}, follow=True)

        updated_place_1 = Place.objects.get(pk=1)

        # db updated?
        self.assertEqual('awesome', updated_place_1.notes)

        self.assertEqual(response.context['place'], updated_place_1)
        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/place_detail.html')

        # and correct data shown on page?
        text_rendered = str(response.content)
        assert 'cool' not in text_rendered   # The old text is gone
        assert 'awesome' in text_rendered    # new text added


    def test_add_notes(self):

        response = self.client.post(reverse('place_details', kwargs={'place_pk':4}), {'notes':'yay'}, follow=True)

        updated_place_4 = Place.objects.get(pk=4)

        # db updated?
        self.assertEqual('yay', updated_place_4.notes)

        # Correct object used in response?
        self.assertEqual(response.context['place'], updated_place_4)
        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/place_detail.html')

        # and correct data shown on page?
        text_rendered = str(response.content)
        assert 'yay' in text_rendered    # new text added


    def test_add_date_visited(self):

        date_visited = '2014-01-01'

        response = self.client.post(reverse('place_details', kwargs={'place_pk':4}), {'date_visited': date_visited}, follow=True)

        updated_place_4 = Place.objects.get(pk=4)

        # Database updated correctly?
        self.assertEqual(updated_place_4.date_visited.isoformat(), date_visited)   # .isoformat is YYYY-MM-DD

        # Right object sent to template?
        self.assertEqual(response.context['place'], updated_place_4)

        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/place_detail.html')

        # and correct data shown on page?
        text_rendered = str(response.content)
        assert date_visited in text_rendered
