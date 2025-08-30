from django.utils import timezone
from .models import BirthdayCelebrant
from .utils import send_birthday_email

def check_and_send_birthday_emails():
    today = timezone.now().date()

    celebrants = BirthdayCelebrant.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day
    ).filter(
        Q(last_celebrated_year__isnull=True) | ~Q(last_celebrated_year=today.year)
    )

    for celebrant in celebrants:
        if celebrant.user:
            send_birthday_email(celebrant.user)
        celebrant.last_celebrated_year = today.year
        celebrant.save()
