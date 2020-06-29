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
    list_display = ['__str__', 'is_solution', 'is_baseline', 'timestamp', 'get_ap', 'get_ap_public']
    #      'mean_average_precision_total',  'mean_average_precision_leaderboard',\
    #  'ap50_leaderboard', 'ap75_leaderboard', 'aps_leaderboard', 'apm_leaderboard', 'apl_leaderboard', 'ap50_total', 'ap75_total']
    readonly_fields = ['timestamp']
    ordering = ['-is_solution', '-is_baseline', '-timestamp']
    actions = [recompute_mean_average_precision]

    def get_ap(self, obj):
        try:
            return obj.submissionmetrics_set.filter(metric_type = "hidden")[0].ap
        except:
            return 0
    get_ap.admin_order_field  = 'ap-hidden'  #Allows column order sorting
    get_ap.short_description = 'AP Full'  #Renames column head
    def get_ap_public(self, obj):
        try:
            return obj.submissionmetrics_set.filter(metric_type = "public")[0].ap
        except:
            return 0
    get_ap_public.admin_order_field  = 'ap-public'  #Allows column order sorting
    get_ap_public.short_description = 'AP 30 %'  #Renames column head



admin.site.register(ProjectSubmission, ProjectSubmissionAdmin)
admin.site.register(LeaderboardSettings)
