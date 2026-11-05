from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Role
from accounts.services.users import grant_role

User = get_user_model()


class Command(BaseCommand):
    help = "Concede um papel a um usuário."

    def add_arguments(self, parser):
        parser.add_argument("email")
        parser.add_argument("role", choices=Role.Name.values)

    def handle(self, *args, **options):
        user = User.objects.filter(email=options["email"].lower()).first()
        if user is None:
            raise CommandError("Usuário não encontrado.")
        grant_role(user=user, name=options["role"])
        self.stdout.write(self.style.SUCCESS("Papel concedido."))
