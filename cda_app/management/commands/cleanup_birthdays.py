from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import BirthdayCelebrant

class Command(BaseCommand):
    help = 'Resets last_celebrated_year for birthdays that are not today'

    def handle(self, *args, **options):
        today = timezone.now().date()
        # Reset last_celebrated_year for all celebrants except those whose birthday is today
        BirthdayCelebrant.objects.exclude(
            date_of_birth__month=today.month,
            date_of_birth__day=today.day
        ).update(last_celebrated_year=None)
        
        self.stdout.write(self.style.SUCCESS('Successfully cleaned up birthday celebrations'))