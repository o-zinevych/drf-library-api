from django.db.models.signals import post_save
from django.dispatch import receiver

from borrowings.models import Borrowing
from borrowings.tasks import notify_user_about_borrowing


@receiver(post_save, sender=Borrowing)
def send_borrowing_notification(sender, instance, created, **kwargs):
    if created:
        notify_user_about_borrowing.delay(instance.id)
