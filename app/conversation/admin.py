from django.contrib import admin

from conversation.models import AnswerModel, ConversationModel, EphemeralAnswerModel, PatientModel, RelevantPointModel


admin.site.register(ConversationModel)
admin.site.register(PatientModel)
admin.site.register(RelevantPointModel)
admin.site.register(AnswerModel)
admin.site.register(EphemeralAnswerModel)
