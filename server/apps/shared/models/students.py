from django.db import models


class Student(models.Model):
    student = models.CharField(
        "Наименование группы",
        max_length=255,
        unique=True
    )
    leader = models.BooleanField("Староста группы", default=False)
    institute = models.ForeignKey("Institute", on_delete=models.CASCADE)
    group = models.ForeignKey("Group", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
