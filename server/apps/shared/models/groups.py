from django.db import models


class Group(models.Model):
    group = models.CharField(
        "Наименование группы",
        max_length=5,
        unique=True
    )
    course = models.IntegerField()
    institute = models.ForeignKey("Institute", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
