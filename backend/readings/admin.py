from django.contrib import admin
from .models import Spread, Reading, ReadingCard


@admin.register(Spread)
class SpreadAdmin(admin.ModelAdmin):
    list_display = ("name", "name_cn", "card_count", "category", "difficulty", "sort_order")
    list_filter = ("category", "difficulty")
    search_fields = ("name", "name_cn")


class ReadingCardInline(admin.TabularInline):
    model = ReadingCard
    extra = 0


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ("id", "mode", "spread_type", "created_at")
    list_filter = ("mode", "spread_type")
    inlines = [ReadingCardInline]
