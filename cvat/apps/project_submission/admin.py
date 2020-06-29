from django.contrib import admin

from .models import ProjectSubmission, LeaderboardSettings

import logging

logger = logging.getLogger(__name__)

def recompute_mean_average_precision(modeladmin, request, queryset):
    if not ProjectSubmission.objects.filter(is_solution=True).exists():
        return
    for submission in queryset:
        try:
            submission.update_mean_average_precision()
        except Exception as e:
            # if a submission has json that for some reason can't be parsed
            logger.error('Failed to update mean average precision for submission' + str(submission) + ': '+str(e))

recompute_mean_average_precision.short_description = 'Recompute MAP based on the solution file.'

class ProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_solution', 'is_baseline', 'timestamp', 'ap_total',  'ap_lb',\
     'ap50_lb', 'ap75_lb', 'aps_lb', 'apm_lb', 'apl_lb', 'ap50_total', 'ap75_total', "aps_total",\
         "apm_total", "apl_total"]
    readonly_fields = ['timestamp']
    ordering = ['-is_solution', '-is_baseline', '-timestamp']
    actions = [recompute_mean_average_precision]


admin.site.register(ProjectSubmission, ProjectSubmissionAdmin)
admin.site.register(LeaderboardSettings)
