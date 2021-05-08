from django.core.management.base import BaseCommand

from app.tele_bot import main


class Command(BaseCommand):

    help = "Start telegram bot"

    def add_arguments(self, parser):
        # Positional arguments
        # parser.add_argument('poll_ids', nargs='+', type=int)
        parser.add_argument("--bot_name", action="append", type=str)

    def handle(self, *args, **options):
        main()
