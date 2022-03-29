from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from datetime import date, timedelta

EXPIRE_PERIOD_DAYS = 365

class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        for user in User.objects.filter(groups__name="regular_user", 
                                        date_joined__lte=date.today() - 
                                        timedelta(days=EXPIRE_PERIOD_DAYS)).all():
            user.is_active = False
            user.save()
            count += 1
        self.stdout.write(f"expired {count} users") 

