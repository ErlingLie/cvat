import os

from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models, transaction


from .eval_detection_coco import compute_submission_map
from .validators import validate_json_formatted

User = get_user_model()

class SubmissionMetrics(models.Model):
    submission = models.ForeignKey("ProjectSubmission", on_delete=models.CASCADE,
    default = 1)
    metric_type = models.CharField(verbose_name="Metric type", max_length=10,
    default="hidden")
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

    ar1 = models.FloatField(
        default = None,
        null= True,
        verbose_name= "AR 1"
    )
    ar10 = models.FloatField(
        default = None,
        null= True,
        verbose_name= "AR 10"
    )
    ar100 = models.FloatField(
        default = None,
        null= True,
        verbose_name= "AR 100"
    )
    ars = models.FloatField(
        default = None,
        null= True,
        verbose_name= "AR small"
    )
    arm = models.FloatField(
        default = None,
        null= True,
        verbose_name= "AR Medium"
    )
    arl = models.FloatField(
        default = None,
        null= True,
        verbose_name= "AR Large"
    )

    def update_metrics(self, ap_array):
        self.ap    = ap_array[0]
        self.ap50  = ap_array[1]
        self.ap75  = ap_array[2]
        self.aps   = ap_array[3]
        self.apm   = ap_array[4]
        self.apl   = ap_array[5]
        self.ar1   = ap_array[6]
        self.ar10  = ap_array[7]
        self.ar100 = ap_array[8]
        self.ars   = ap_array[9]
        self.arm   = ap_array[10]
        self.arl   = ap_array[11]
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

    is_solution = models.BooleanField(
        default=False,
    )
    is_baseline = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Project Submission"
        verbose_name_plural = "Project Submissions"

    @property
    def hidden_submission(self):
        metrics = self.submissionmetrics_set.filter(metric_type="hidden")
        if len(metrics) == 0:
            return None
        assert len(metrics) == 1
        return metrics[0]

    @property
    def public_submission(self):
        metrics = self.submissionmetrics_set.filter(metric_type="public")
        if len(metrics) == 0:
            return None
        assert len(metrics) == 1
        return metrics[0]


    def update_mean_average_precision(self):
        with transaction.atomic():
            solution = ProjectSubmission.objects.filter(is_solution=True)
            if not solution.exists():
                self.save()
                return
            if self.is_solution:
                self.save()
                return
            # if, for some reason there are multiple entries marked 'is_solution=True'
            # Then this will get the one updated last
            solution = solution.order_by('-timestamp').first()
            map_tot, map_lb = compute_submission_map(self.submission_json, solution.submission_json)

            self.hidden_submission.update_metrics(map_tot)
            self.public_submission.update_metrics(map_lb)
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
