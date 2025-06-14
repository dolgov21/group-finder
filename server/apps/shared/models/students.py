from django.db import models


class Student(models.Model):
    name = models.CharField(
        "Наименование группы",
        max_length=255,
        unique=True
    )
    is_leader = models.BooleanField("Староста группы", default=False)
    institute = models.ForeignKey("Institute", on_delete=models.CASCADE)
    group = models.ForeignKey("Group", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return f"Student(id={self.id}, name={repr(self.name)}, is_leader={repr(self.is_leader)}, institute={repr(self.institute)}, group={repr(self.group)})"