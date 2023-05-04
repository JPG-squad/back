from django.core.management.base import BaseCommand

from app.opensearch import open_search
from conversation.models import ConversationModel


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
                c_to_index = {
                    "object_type": "conversation",
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "patient_id": c.patient.id,
                    "status": c.status,
                    "draft": c.draft,
                    "created_at": c.created_at,
                    "updated_at": c.updated_at,
                    "conversation": c.conversation,
                    "duration": c.duration,
                }
                try:
                    open_search.index(
                        index="jpg.object", id=f"{c_to_index['object_type']}-{c_to_index['id']}", body=c_to_index
                    )
                    self.stdout.write(self.style.SUCCESS(f"Indexed conversation {c_to_index['id']}"))
                except Exception:
                    self.stdout.write(self.style.ERROR(f"Error indexing conversation {c_to_index['id']}"))

            msg = f'{len(conversations)} Conversations indexed to opensearch correctly!'
            self.stdout.write(self.style.SUCCESS(msg))
            return msg

        else:
            msg = f'Ojbect "{object}" not supported.'
            self.stdout.write(self.style.ERROR(msg))
            return msg
