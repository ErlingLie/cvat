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
    readonly_fields = ['timestamp']
    ordering = ['-is_solution', '-is_baseline', '-timestamp']
    actions = [recompute_mean_average_precision]

    def get_ap(self, obj):
        if obj.hidden_submission is None:
            return 0
        return obj.hidden_submission.ap
    get_ap.admin_order_field  = 'ap-hidden'  #Allows column order sorting
    get_ap.short_description = 'AP Full'  #Renames column head
    def get_ap_public(self, obj):
        if obj.public_submission is None:
            return 0
        return obj.public_submission.ap
    get_ap_public.admin_order_field  = 'ap-public'  #Allows column order sorting
    get_ap_public.short_description = 'AP 30 %'  #Renames column head



admin.site.register(ProjectSubmission, ProjectSubmissionAdmin)
admin.site.register(LeaderboardSettings)
