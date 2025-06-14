from server.apps.shared.models import Institute, Group, Student

def clear_all_tables() -> None:
    Institute.objects.all().delete()
    Group.objects.all().delete()
    Student.objects.all().delete()