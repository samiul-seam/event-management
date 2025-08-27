from django.db import models

# Create your models here.

# events/models.py
from django.db import models

class Participant(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField(unique=True)
    def __str__(self):
        return f"{self.name} ({self.email})"


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('webinar', 'Webinar'),
        ('meetup', 'Meetup'),
    ]
    name = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        unique=True
    )
    description = models.TextField(blank=True , null=True)

    def __str__(self):
        return self.get_name_display()

class Event(models.Model):
    included_in = models.ManyToManyField(Participant , related_name= 'participants')
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=250)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="events")

    def __str__(self):
        return self.name

