from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import LeaderboardSettings

User = get_user_model()

@receiver(post_save, sender=User)
def update_submission_map(sender, instance, created, **kwargs):
    """automatically create associated leaderboard settings when a user is created
    """
    if created:
        LeaderboardSettings.objects.create(user=instance)
