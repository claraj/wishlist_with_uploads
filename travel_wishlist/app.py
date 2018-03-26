from django.apps import AppConfig

class PlacesConfig(AppConfig):

    name = 'travel_wishlist'
    verbose_name = 'Travel Wishlist App Config'

    def ready(self):
        import travel_wishlist.signals
