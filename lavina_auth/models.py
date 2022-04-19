from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User
from django.db import models
from .elevation_basic import get_relief
from django.contrib.gis.geos import Point

class PlaceType(models.Model):
    type = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.type

class Place(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.RESTRICT)
    place_type = models.ForeignKey('PlaceType', on_delete=models.RESTRICT)
    geometry = gis_models.PolygonField()
    heighest_point = gis_models.PointField(blank=True, null=True)
    heighest_elevation = models.IntegerField(blank=True, null=True)


    def save(self, *args, **kwargs):
        relief = get_relief(self.geometry.extent)
        self.heighest_elevation = relief[0]["elevation"]
        self.heighest_point = Point(relief[0]["coords"][0], relief[0]["coords"][1])
        super(Place, self).save(*args, **kwargs)


    def __str__(self) -> str:
        return f"{self.name} {self.place_type}"