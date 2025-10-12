from django.apps import AppConfig


class TeacherDashConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'teacher_dash'

    def ready(self):
        """
        Import signal handlers when the app is ready.
        This ensures signals are registered and active.
        """
        import teacher_dash.signals  # noqa: F401
