from django.db.models.signals import post_save, pre_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from events.models import Event , RSVP



@receiver(m2m_changed, sender=Event.participants.through)
def notify_participants_on_event_creation(sender, instance, action, **kwargs):
    if action == 'post_add':
        assigned_emails = [user.email for user in instance.participants.all()]

        send_mail(
            subject="New Event Assigned",
            message=f"You have been assigned to the event: {instance.name} on {instance.location} at {instance.date} ",
            from_email="mdsamiulhaque682@gmail.com",
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
            f"Hi {user.username}, you have RSVP'd for the event: {event.name} on {event.date}.",
            "mdsamiulhaque682@gmail.com",
            recipient_list=[user.email],
            fail_silently=False
        )