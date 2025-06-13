from django.db import models

class StudentArchive(models.Model):
    institute = models.CharField(max_length=255, blank=True)
    course = models.IntegerField(blank=True, null=True)
    group = models.CharField(max_length=255, blank=True)
    student = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Архив студентов"