# Generated by Django 2.2.13 on 2020-06-29 10:59

import cvat.apps.project_submission.validators
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubmissionMetrics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ap', models.FloatField(default=None, null=True, verbose_name='AP')),
                ('ap50', models.FloatField(default=None, null=True, verbose_name='AP50')),
                ('ap75', models.FloatField(default=None, null=True, verbose_name='AP75')),
                ('aps', models.FloatField(default=None, null=True, verbose_name='AP small')),
                ('apm', models.FloatField(default=None, null=True, verbose_name='AP medium')),
                ('apl', models.FloatField(default=None, null=True, verbose_name='AP large')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectSubmission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('submission_json', models.FileField(upload_to='submissions/%Y', validators=[django.core.validators.FileExtensionValidator(['json']), cvat.apps.project_submission.validators.validate_json_formatted], verbose_name='Submission JSON')),
                ('timestamp', models.DateTimeField(auto_now=True, verbose_name='Submission time')),
                ('is_solution', models.BooleanField(default=False)),
                ('is_baseline', models.BooleanField(default=False)),
                ('hidden_metrics', models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='hidden_metrics', to='project_submission.SubmissionMetrics')),
                ('public_metrics', models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='public_metrics', to='project_submission.SubmissionMetrics')),
                ('user', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_submissions', to=settings.AUTH_USER_MODEL, verbose_name='Group')),
            ],
            options={
                'verbose_name': 'Project Submission',
                'verbose_name_plural': 'Project Submissions',
                'ordering': ['-public_metrics__ap'],
            },
        ),
        migrations.CreateModel(
            name='LeaderboardSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_on_leaderboard', models.BooleanField(default=True, verbose_name='Show this group on the leaderboard')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='leaderboard_settings', to=settings.AUTH_USER_MODEL, verbose_name='Group')),
            ],
            options={
                'verbose_name': 'Leaderboard Settings',
                'verbose_name_plural': 'Leaderboard Settings',
            },
        ),
    ]
