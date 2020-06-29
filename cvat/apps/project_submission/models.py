import os

from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models, transaction


from .eval_detection_coco import compute_submission_map
from .validators import validate_json_formatted

User = get_user_model()

class SubmissionMetrics(models.Model):
    ap = models.FloatField(
        default=None,
        null=True,
        verbose_name = "AP"
    )
    ap50 = models.FloatField(
        default=None,
        null=True,
        verbose_name = "AP50"
    )
    ap75 = models.FloatField(
        default=None,
        null=True,
        verbose_name = "AP75"
    )
    aps = models.FloatField(
        default=None,
        null=True,
        verbose_name = "AP small"
    )
    apm = models.FloatField(
        default=None,
        null=True,
        verbose_name = "AP medium"
    )
    apl = models.FloatField(
        default=None,
        null=True,
        verbose_name = "AP large"
    )

    def update_metrics(self, ap_array):
        self.ap   = ap_array[0]
        self.ap50 = ap_array[1]
        self.ap75 = ap_array[2]
        self.aps  = ap_array[3]
        self.apm  = ap_array[4]
        self.apl  = ap_array[5]
        self.save()



class ProjectSubmission(models.Model):
    id = models.AutoField(primary_key=True)
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
    hidden_metrics = models.OneToOneField(
        SubmissionMetrics, on_delete=models.CASCADE,
        null =True,
        blank=True,
        default=1,
        related_name = "hidden_metrics",
    )
    public_metrics = models.OneToOneField(
        SubmissionMetrics, on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=1,
        related_name="public_metrics"
    )
    is_solution = models.BooleanField(
        default=False,
    )
    is_baseline = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["-public_metrics__ap"]
        verbose_name = "Project Submission"
        verbose_name_plural = "Project Submissions"


    def update_mean_average_precision(self):
        with transaction.atomic():
            solution = ProjectSubmission.objects.filter(is_solution=True)
            self.hidden_metrics = SubmissionMetrics()
            self.public_metrics = SubmissionMetrics()
            if not solution.exists():
                self.hidden_metrics.update_metrics([None for i in range(12)])
                self.public_metrics.update_metrics([None for i in range(12)])
                self.save()
                return

            # if, for some reason there are multiple entries marked 'is_solution=True'
            # Then this will get the one updated last
            solution = solution.order_by('-timestamp').first()
            map_tot, map_lb = compute_submission_map(self.submission_json, solution.submission_json)
            self.public_metrics.update_metrics(map_lb)
            self.hidden_metrics.update_metrics(map_tot)
            self.save()

    def __str__(self):
        if self.is_solution:
            return 'Solution'
        return str(os.path.basename(self.submission_json.name)) + ' from ' + str(self.user)




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
