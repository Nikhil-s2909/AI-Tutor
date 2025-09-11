
from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=200, unique=True)
    syllabus = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Syllabus(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class ClassTiming(models.Model):
    subject = models.CharField(max_length=200)
    day = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.subject} ({self.day} {self.start_time}-{self.end_time})"
