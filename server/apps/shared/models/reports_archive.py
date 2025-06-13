from django.db import models


class ReportsArchive(models.Model):
    report_content = models.TextField("Отчет в текстовом представлении")
    report_json = models.JSONField("Отчёт в JSON формате")

    class Meta:
        verbose_name = "Архив отчётов"