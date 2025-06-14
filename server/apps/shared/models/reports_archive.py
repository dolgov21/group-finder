from django.db import models


class ReportsArchive(models.Model):
    report_content = models.TextField("Отчет в текстовом представлении")
    report_json = models.JSONField("Отчёт в JSON формате")

    class Meta:
        verbose_name = "Архив отчётов"

    def __str__(self):
        return f"ReportsArchive(report_content={repr(self.report_content)}, report_json={repr(self.report_json)})"