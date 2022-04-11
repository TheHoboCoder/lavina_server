from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User
from django.db import models
from .elevation_basic import get_relief

class PlaceType(models.Model):
    type = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.type

class Place(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.RESTRICT)
    place_type = models.ForeignKey('PlaceType', on_delete=models.RESTRICT)
    geometry = gis_models.PolygonField()
    relief_map = models.JSONField(blank=True, null=True)

    # def save(self):
    #     self.relief_map = get_relief(self)
    #     super(Place, self).save()


    def __str__(self) -> str:
        return f"{self.name} {self.place_type}"