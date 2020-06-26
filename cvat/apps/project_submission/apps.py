from django.apps import AppConfig

class ProjectSubmissionConfig(AppConfig):
    """config for project_submission
    The ready() function is necessary for project_submission.signals to run
    Which is required to have users' LeaderboardSettings created when the user is created
    """
    name = 'cvat.apps.project_submission'
    def ready(self):
        from . import signals
