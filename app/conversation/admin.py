from django.contrib import admin

from conversation.models import AnswerVersionModel, ConversationModel, PatientModel, RelevantPointModel

admin.site.register(ConversationModel)
admin.site.register(PatientModel)
admin.site.register(RelevantPointModel)
admin.site.register(AnswerVersionModel)
