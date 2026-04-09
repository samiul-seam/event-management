from django.db.models.signals import post_save, pre_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from events.models import Event , RSVP
from django.conf import settings




@receiver(m2m_changed, sender=Event.participants.through)
def notify_participants_on_event_creation(sender, instance, action, **kwargs):
    if action == 'post_add':
        assigned_emails = [user.email for user in instance.participants.all()]

        send_mail(
            subject="New Event Assigned",
            message = f"🎉 Congratulations! 🎉\n\nYou have been successfully assigned to the following event:\n📌 Event: {instance.name}\n📍 Location: {instance.location}\n📅 Date: {instance.date}\nWe look forward to seeing you there! ",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=assigned_emails,
            fail_silently=False
        )

@receiver(post_save, sender=RSVP)
def notify_participant_on_rsvp(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        event = instance.event

        send_mail(
            "RSVP Confirmation",
            f"Hi {user.username}, you have RSVP'd for the event:\n📌 Event: {event.name}\n📅 Date: {event.date}\n📍 Location:{event.location}.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False
        )