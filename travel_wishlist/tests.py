import tempfile
import filecmp
import os 

from django.test import TestCase
from django.urls import reverse
from django.test import override_settings

from django.contrib.auth.models import User
from .models import Place

from PIL import Image 


class TestViewHomePageIsEmptyList(TestCase):

    fixtures = ['test_users']

    def setUp(self):
        user = User.objects.get(pk=1)
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
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

    def test_view_wishlist(self):
        response = self.client.get(reverse('place_list'))
        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # What data was sent to the template?
        data_rendered = list(response.context['places'])
        # What data is in the database? Get all of the items for this user where visited = False
        data_expected = list(Place.objects.filter(user=self.user).filter(visited=False))

        # Is it the same?
        self.assertCountEqual(data_rendered, data_expected)


    def test_view_places_visited(self):
        response = self.client.get(reverse('places_visited'))
        # Check correct template was used
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')

        # What data was sent to the template?
        data_rendered = list(response.context['visited'])
        # What data is in the database? Get all of the items where visited = false
        data_expected = list(Place.objects.filter(user=self.user).filter(visited=True))
        # Is it the same?
        self.assertCountEqual(data_rendered, data_expected)


class TestAddNewPlace(TestCase):

    # Load this data into the database for all of the tests in this class
    fixtures = ['test_users']

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)

    def test_add_new_unvisited_place_to_wishlist(self):

        response = self.client.post(reverse('place_list'), { 'name': 'Tokyo', 'visited': False }, follow=True)

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
        response =  self.client.post(reverse('place_list'), { 'name': 'Yosemite', 'visited': False }, follow=True)

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

        response = self.client.post(reverse('place_list'), { 'name': 'Tokyo', 'visited': True }, follow=True)

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

    fixtures = ['test_places', 'test_users']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)


    def test_mark_unvisited_place_as_visited(self):

        response = self.client.post(reverse('place_was_visited'), {'pk': 2}, follow=True)
        # Assert redirected to place list
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        # Check database for correct data
        place = Place.objects.get(pk=2)
        self.assertTrue(place.visited)


    def test_mark_non_existent_place_as_visited_returns_404(self):
        response = self.client.post(reverse('place_was_visited'), {'pk': 200}, follow=True)
        self.assertEqual(404, response.status_code)


    def test_visit_someone_else_place_not_authorized(self):
        response = self.client.post(reverse('place_was_visited'), {'pk': 5}, follow=True)
        self.assertEqual(403, response.status_code)  # 403 Forbidden


class TestDeletePlace(TestCase):

    fixtures = ['test_places', 'test_users']

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)

    def delete_own_place():
        response = self.client.post(reverse('delete', kwargs={'place_pk': 2}), follow=True)
        place_2 = Place.objects.filter(pk=2)
        assert place_2 is None 

    def delete_someone_else_place_not_auth():
        response = self.client.post(reverse('delete', kwargs={'place_pk': 6}), follow=True)
        self.assertEqual(401, response.status_code)
        place_5 = Place.objects.filter(pk=5)
        assert place_5 is not None 


class TestPlaceDetail(TestCase):
    # Load this data into the database for all of the tests in this class
    fixtures = ['test_places', 'test_users']

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)


    def test_modify_someone_else_place_details_not_authorized(self):
        response = self.client.post(reverse('place_details', kwargs={'place_pk':5}), {'notes':'awesome'}, follow=True)
        self.assertEqual(403, response.status_code)   # 403 Forbidden 
        

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


class TestImageUpload(TestCase):

    fixtures = ['test_users', 'test_places']

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)
        self.MEDIA_ROOT = tempfile.mkdtemp()
        

    def tearDown(self):
        print('todo delete temp directory, temp image')


    def create_temp_image_file(self):
        handle, tmp_img_file = tempfile.mkstemp(suffix='.jpg')
        img = Image.new('RGB', (10, 10) )
        img.save(tmp_img_file, format='JPEG')
        return tmp_img_file


    def test_upload_new_image_for_own_place(self):
        
        img_file_path = self.create_temp_image_file()

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
            with open(img_file_path, 'rb') as img_file:
                resp = self.client.post(reverse('place_details', kwargs={'place_pk': 1} ), {'photo': img_file }, follow=True)
                
                assert resp.status_code == 200

                place_1 = Place.objects.get(pk=1)
                img_file_name = os.path.basename(img_file_path)
                expected_uploaded_file_path = os.path.join(self.MEDIA_ROOT, 'user_images', img_file_name)

                assert os.path.exists(expected_uploaded_file_path)
                assert place_1.photo
                assert filecmp.cmp( img_file_path,  expected_uploaded_file_path )


    def test_change_image_for_own_place_expect_old_deleted(self):
        
        first_img_file_path = self.create_temp_image_file()
        second_img_file_path = self.create_temp_image_file()

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
            with open(first_img_file_path, 'rb') as first_img_file:

                resp = self.client.post(reverse('place_details', kwargs={'place_pk': 1} ), {'photo': first_img_file }, follow=True)

                place_1 = Place.objects.get(pk=1)

                first_uploaded_image = place_1.photo.name

                with open(second_img_file_path, 'rb') as second_img_file:
                    resp = self.client.post(reverse('place_details', kwargs={'place_pk':1}), {'photo': second_img_file}, follow=True)

                    # first file should not exist 
                    # second file should exist 

                    place_1 = Place.objects.get(pk=1)

                    second_uploaded_image = place_1.photo.name

                    first_path = os.path.join(self.MEDIA_ROOT, first_uploaded_image)
                    second_path = os.path.join(self.MEDIA_ROOT, second_uploaded_image)

                    assert not os.path.exists(first_path)
                    assert os.path.exists(second_path)


    def test_upload_image_for_someone_else_place(self):

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
  
            img_file = self.create_temp_image_file()
            with open(img_file, 'rb') as image:
                resp = self.client.post(reverse('place_details', kwargs={'place_pk': 5} ), {'photo': image }, follow=True)
                assert 403, resp.status_code

                place_5 = Place.objects.get(pk=5)
                assert not place_5.photo


    def test_delete_place_with_image_image_deleted(self):
        
        img_file_path = self.create_temp_image_file()

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
            with open(img_file_path, 'rb') as img_file:
                resp = self.client.post(reverse('place_details', kwargs={'place_pk': 1} ), {'photo': img_file }, follow=True)
                
                assert resp.status_code == 200

                place_1 = Place.objects.get(pk=1)
                img_file_name = os.path.basename(img_file_path)
                
                uploaded_file_path = os.path.join(self.MEDIA_ROOT, 'user_images', img_file_name)

                # delete place 1 

                place_1 = Place.objects.get(pk=1)
                place_1.delete()

                assert not os.path.exists(uploaded_file_path)
               
