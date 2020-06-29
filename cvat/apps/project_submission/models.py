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
    ap_lb = models.FloatField(
        default=None,
        null=True,
        verbose_name="Leaderboard MAP"
    )
    ap_total = models.FloatField(
        default=None,
        null=True,
        verbose_name="Total MAP"
    )
    ap50_lb = models.FloatField(
        default=None,
        null=True,
        verbose_name = "Leaderboard AP50"
    )
    ap75_lb = models.FloatField(
        default=None,
        null=True,
        verbose_name = "Leaderboard AP75"
    )
    aps_lb= models.FloatField(
        default=None,
        null=True,
        verbose_name = "Leaderboard AP small"
    )
    apm_lb = models.FloatField(
        default=None,
        null=True,
        verbose_name = "Leaderboard AP medium"
    )
    apl_lb = models.FloatField(
        default=None,
        null=True,
        verbose_name = "Leaderboard AP large"
    )
    ap50_total = models.FloatField(
        default=None,
        null=True,
        verbose_name = "Total AP 50"
    )
    ap75_total = models.FloatField(
        default=None,
        null=True,
        verbose_name = "Total AP 75"
    )
    aps_total = models.FloatField(
        default=None,
        null=True,
        verbose_name = "Total AP 75"
    )
    apm_total = models.FloatField(
        default=None,
        null=True,
        verbose_name = "Total AP 75"
    )
    apl_total = models.FloatField(
        default=None,
        null=True,
        verbose_name = "Total AP 75"
    )
    is_solution = models.BooleanField(
        default=False,
    )
    is_baseline = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["-ap_lb", "id"]
        verbose_name = "Project Submission"
        verbose_name_plural = "Project Submissions"


    def update_metrics(self, lb, tot):
        self.ap_lb      = lb[0]
        self.ap50_lb    = lb[1]
        self.ap75_lb    = lb[2]
        self.aps_lb     = lb[3]
        self.apm_lb     = lb[4]
        self.apl_lb     = lb[5]
        self.ap_total   = tot[0]
        self.ap50_total = tot[1]
        self.ap75_total = tot[2]
        self.aps_total  = tot[3]
        self.apm_total  = tot[4]
        self.apl_total  = tot[5]

    def update_mean_average_precision(self):
        with transaction.atomic():
            solution = ProjectSubmission.objects.filter(is_solution=True)
            if not solution.exists():
                self.update_metrics([None for i in range(6)], [None for i in range(6)])
                self.save()
                return

            # if, for some reason there are multiple entries marked 'is_solution=True'
            # Then this will get the one updated last
            solution = solution.order_by('-timestamp').first()
            map_tot, map_lb = compute_submission_map(self.submission_json, solution.submission_json)
            self.update_metrics(map_lb, map_tot)
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
