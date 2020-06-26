

from django.contrib.auth import get_user_model
from django.forms import ModelForm

from .models import ProjectSubmission, LeaderboardSettings

User = get_user_model()

class ProjectSubmissionForm(ModelForm):
    class Meta:
        model=ProjectSubmission
        exclude=["user", "timestamp", "mean_average_precision_total", "mean_average_precision_leaderboard", "is_solution", "is_baseline"]



class LeaderboardSettingsForm(ModelForm):
    class Meta:
        model=LeaderboardSettings
        exclude=["user"]
