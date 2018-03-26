from django.db import models
from django.contrib.auth.models import User


class Place(models.Model):
    user = models.ForeignKey('auth.User', null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    visited = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    date_visited = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='images/', blank=True, null=True)


    def __str__(self):
        return '%d: %s visited? %s on %s\nPhoto %s' % (self.pk, self.name, self.visited, self.date_visited, self.photo.url if self.photo else 'no photo' )
