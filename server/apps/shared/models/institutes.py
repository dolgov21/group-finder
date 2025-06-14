from django.db import models 


class Institute(models.Model):
    name = models.CharField(
        "Наименование института",
        max_length=255,
        unique=True
    )
    institute_code = models.IntegerField(
        "Порядковый номер института",
        unique=True
    )

    class Meta:
        verbose_name = "Институт"
        verbose_name_plural = "Институты"

    def __str__(self):
        return f"Institute(id={self.id}, name={repr(self.name)}, institute_code={self.institute_code})"