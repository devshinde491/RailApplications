from django.core.management.base import BaseCommand
from django.db import models




class Command(BaseCommand):
    help = "Adds railway stations to the database"

    def handle(self, *args, **kwargs):
        stations = [
            {"name": "Mumbai Central", "code": "MMCT", "city": "Mumbai", "state": "Maharashtra", "zone": "WR", "station_type": "Junction", "number_of_platforms": 5},
            {"name": "Chhatrapati Shivaji Terminus", "code": "CSTM", "city": "Mumbai", "state": "Maharashtra", "zone": "CR", "station_type": "Terminus", "number_of_platforms": 18},
            {"name": "New Delhi", "code": "NDLS", "city": "Delhi", "state": "Delhi", "zone": "NR", "station_type": "Junction", "number_of_platforms": 16},
            {"name": "Kolkata Howrah Junction", "code": "HWH", "city": "Kolkata", "state": "West Bengal", "zone": "ER", "station_type": "Junction", "number_of_platforms": 23},
            {"name": "Chennai Central", "code": "MAS", "city": "Chennai", "state": "Tamil Nadu", "zone": "SR", "station_type": "Junction", "number_of_platforms": 17},
        ]

        for station in stations:
            from railapp.models import Station
            Station.objects.get_or_create(
                name=station["name"],
                code=station["code"],
                city=station["city"],
                state=station["state"],
                zone=station["zone"],
                station_type=station["station_type"],
                number_of_platforms=station["number_of_platforms"],
            )

        self.stdout.write(self.style.SUCCESS("Stations added successfully!"))
