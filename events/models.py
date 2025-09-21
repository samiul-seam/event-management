from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    participants = models.ManyToManyField(User, through='RSVP', blank=True, related_name='events')

    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=250)
    asset = models.ImageField(
        upload_to='tasks_asset', blank=True, null=True,
        default='tasks_asset/default_img.jpg'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )

    class Meta:
        ordering = ['-date', 'time']

    def __str__(self):
        return f"{self.name} — {self.date} {self.time}"

class RSVP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rsvps')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event') 

    def __str__(self):
        return f"{self.user.username} RSVPed to {self.event.name}"