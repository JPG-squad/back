from django.contrib import admin

from conversation.models import ConversationModel
from conversation.models import PatientModel
from conversation.models import RelevantPointModel
from conversation.models import AnswerVersionModel

admin.site.register(ConversationModel)
admin.site.register(PatientModel)
admin.site.register(RelevantPointModel)
admin.site.register(AnswerVersionModel)
