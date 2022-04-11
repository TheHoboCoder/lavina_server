from lavina_auth.elevation_basic import get_relief
from lavina_auth.models import Place
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point

class Command(BaseCommand):
    def handle(self, *args, **options):
        for place in Place.objects.all():
            relief = get_relief(place.geometry.extent)
            place.relief_map = relief[1]
            place.heighest_elevation = relief[0]["elevation"]
            place.heighest_point = Point(relief[0]["coords"][0], relief[0]["coords"][1])
            place.save()