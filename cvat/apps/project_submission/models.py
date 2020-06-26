import os

from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models, transaction


from .eval_detection_coco import compute_submission_map
from .validators import validate_json_formatted

User = get_user_model()


class ProjectSubmission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        verbose_name="Group",
        related_name="project_submissions"
    )
    submission_json = models.FileField(
        upload_to="submissions/%Y",
        validators=[FileExtensionValidator(['json']), validate_json_formatted],
        verbose_name="Submission JSON"
    )
    timestamp = models.DateTimeField(
        auto_now=True,
        verbose_name="Submission time"
    )
    mean_average_precision_leaderboard = models.FloatField(
        default=None,
        null=True,
        verbose_name="Leaderboard MAP"
    )
    mean_average_precision_total = models.FloatField(
        default=None,
        null=True,
        verbose_name="Total MAP"
    )
    is_solution = models.BooleanField(
        default=False,
    )
    is_baseline = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["-mean_average_precision_leaderboard", "id"]
        verbose_name = "Project Submission"
        verbose_name_plural = "Project Submissions"


    def update_mean_average_precision(self):
        with transaction.atomic():
            solution = ProjectSubmission.objects.filter(is_solution=True)
            if not solution.exists():
                self.mean_average_precision_leaderboard = None
                self.mean_average_precision_total = None
                self.save()
                return

            # if, for some reason there are multiple entries marked 'is_solution=True'
            # Then this will get the one updated last
            solution = solution.order_by('-timestamp').first()
            map_tot, map_lb = compute_submission_map(self.submission_json, solution.submission_json)
            self.mean_average_precision_leaderboard = map_lb
            self.mean_average_precision_total = map_tot
            self.save()

    def __str__(self):
        if self.is_solution:
            return 'Solution'
        return 'Submission ' + str(os.path.basename(self.submission_json.name)) + ' from ' + str(self.user) + ' submitted at ' + str(self.timestamp)




class LeaderboardSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="Group",
        related_name="leaderboard_settings"
    )

    show_on_leaderboard = models.BooleanField(
        default=True,
        verbose_name="Show this group on the leaderboard"
    )

    class Meta:
        verbose_name = "Leaderboard Settings"
        verbose_name_plural = "Leaderboard Settings"

    def __str__(self):
        return 'Leaderboard settings for '+str(self.user)
