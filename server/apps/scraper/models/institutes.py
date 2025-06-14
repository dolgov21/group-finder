from django.db import models 


class Institute(models.Model):
    name = models.CharField(
        "Наименование института",
        max_length=255,
        unique=True
    )
    institute_num = models.IntegerField(
        "Порядковый номер института",
        unique=True
    )

    class Meta:
        verbose_name = "Институт"
        verbose_name_plural = "Институты"
