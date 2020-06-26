from django.core.management.base import BaseCommand
from ...models import ProjectSubmission


class Command(BaseCommand):
    help =  'Recompute MAP based on the solution file.'

    def add_arguments(self, parser):
        return

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting'))

        solutions = ProjectSubmission.objects.filter(is_solution=True)
        submissions = ProjectSubmission.objects.filter(is_solution=False)

        count_solutions = len(solutions)
        count_submissions = len(submissions)
        count_baselines = len(submissions.filter(is_baseline=True))


        if count_solutions == 0:
            self.stdout.write(self.style.ERROR('Error: No entries in the database are marked as solutions. Exiting'))
            return
        if count_solutions > 1:
            self.stdout.write(self.style.NOTICE('Warning: ' +str(count_solutions) + ' entries in the database are marked as solutions. Only the one that was updated most recently is used.'))

        self.stdout.write('Recomputing '+str(count_submissions)+' submissions, of which '+str(count_baselines)+' are marked as baselines')

        for i, submission in enumerate(submissions):
            try:
                self.stdout.write('[Progress: ' + str(i).ljust(5) + 'of ' + str(count_submissions).ljust(5) + ']')
                submission.update_mean_average_precision()
            except Exception as e:
                # if a submission has json that for some reason can't be parsed
                self.stdout.write(self.style.ERROR('\nRecompututation of submission with id '+str(submission.id)+' failed with error:\n'+str(e)))
        print('Finished')
