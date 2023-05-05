from django.core.management.base import BaseCommand

from conversation.models import ConversationModel
from conversation.services.opensearch import open_search_service


class Command(BaseCommand):
    """
    Usage:
        $ python manage.py index --object Conversation
    """

    help = "Index objects of the database to opensearch."

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--object",
            type=str,
            help="Object to index",
        )

    def handle(self, *args, **options):
        object = options["object"]
        if not object:
            msg = "Param --object is required"
            self.stdout.write(self.style.ERROR(msg))
            return msg

        if object.lower() == "conversation":
            self.stdout.write('Indexing objects: "Conversation"')

            conversations = list(ConversationModel.objects.all())

            for c in conversations:
                open_search_service.index_conversation(c)

            msg = f'{len(conversations)} Conversations indexed to opensearch correctly!'
            self.stdout.write(self.style.SUCCESS(msg))
            return msg

        else:
            msg = f'Ojbect "{object}" not supported.'
            self.stdout.write(self.style.ERROR(msg))
            return msg
