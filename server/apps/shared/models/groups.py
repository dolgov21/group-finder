from django.db import models


class Group(models.Model):
    name = models.CharField(
        "Наименование группы",
        max_length=5,
        unique=True
    )
    course = models.IntegerField()
    institute = models.ForeignKey("Institute", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return f"Group(id={self.id}, name={self.name}, course={self.course}, institute={repr(self.institute)})"