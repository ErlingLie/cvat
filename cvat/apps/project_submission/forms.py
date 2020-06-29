

from django.contrib.auth import get_user_model
from django.forms import ModelForm

from .models import ProjectSubmission, LeaderboardSettings

User = get_user_model()

class ProjectSubmissionForm(ModelForm):
    class Meta:
        model=ProjectSubmission
        exclude=["user", "timestamp", "ap_total", "ap_lb", "ap50_lb",\
        "ap75_lb", "aps_lb", "apm_lb", "apl_lb", "ap50_total", "ap75_total", "aps_total",\
            "apm_total", "apl_total", "is_solution", "is_baseline"]



class LeaderboardSettingsForm(ModelForm):
    class Meta:
        model=LeaderboardSettings
        exclude=["user"]
