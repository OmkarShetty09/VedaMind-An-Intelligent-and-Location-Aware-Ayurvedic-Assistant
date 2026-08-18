from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["role", "content", "source_citations", "llm_model", "tokens"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "updated_at", "deleted_at"]
    inlines = [MessageInline]
