from django.core.management.base import BaseCommand
from cryptography.fernet import Fernet

class Command(BaseCommand):
    help = "Gera uma chave Fernet (base64 urlsafe) para DJANGO_PASSWORDS_KEY"

    def handle(self, *args, **options):
        key = Fernet.generate_key()
        self.stdout.write(self.style.SUCCESS("Chave Fernet gerada:"))
        self.stdout.write(key.decode('utf-8'))
        self.stdout.write(self.style.WARNING("Defina DJANGO_PASSWORDS_KEY no .env com essa chave."))
