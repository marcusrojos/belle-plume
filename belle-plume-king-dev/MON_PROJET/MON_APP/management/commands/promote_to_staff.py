from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Promote or demote a user to staff. Usage: python manage.py promote_to_staff --username USER --staff true|false'

    def add_arguments(self, parser):
        parser.add_argument('--username', required=True, help='Username (or email) of the user')
        parser.add_argument('--staff', required=True, choices=['true', 'false'], help='Set to true to promote, false to demote')

    def handle(self, *args, **options):
        username = options['username']
        staff_flag = options['staff'] == 'true'
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"Utilisateur '{username}' introuvable")
        user.is_staff = staff_flag
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Utilisateur '{username}' mis à jour: is_staff={user.is_staff}"))
