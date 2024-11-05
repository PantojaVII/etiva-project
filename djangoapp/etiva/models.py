# etiva/models.py
from django.db import models
from django.utils.text import slugify   

class Participant(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    phone_number = models.CharField(max_length=15)
    slug = models.SlugField(unique=True, blank=True)

    # Defina a relação ManyToMany
    activities = models.ManyToManyField('Activity', blank=True, related_name='participants')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.full_name)
        super(Participant, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name

class ActivityType(models.Model):
    type_name = models.CharField(max_length=100)

    def __str__(self):
        return self.type_name

class Activity(models.Model):
    activity_name = models.CharField(max_length=255)
    activity_date = models.DateField()
    activity_time = models.TimeField()
    responsible_person = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    activity_type = models.ForeignKey(ActivityType, on_delete=models.CASCADE)

    def __str__(self):
        return self.activity_name
