from django.db import models
from cards.models import TarotCard


class Spread(models.Model):
    """Pre-defined tarot spread types with position configurations."""

    class Category(models.TextChoices):
        GLANCE = "glance", "速览"
        CLASSIC = "classic", "经典"
        DEPTH = "depth", "深度"
        RELATION = "relation", "关系"
        DECISION = "decision", "抉择"
        INNER = "inner", "内在"
        TIMING = "timing", "时序"

    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "入门"
        INTERMEDIATE = "intermediate", "进阶"
        ADVANCED = "advanced", "高阶"

    name = models.CharField(max_length=100, unique=True)
    name_cn = models.CharField(max_length=100)
    description = models.TextField()
    description_cn = models.TextField(blank=True, default="")
    card_count = models.IntegerField()
    positions = models.JSONField()  # English position names
    positions_cn = models.JSONField(default=list)
    layout = models.JSONField(default=list)  # [{x, y, rotate?, overlay?}]
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.CLASSIC
    )
    difficulty = models.CharField(
        max_length=20, choices=Difficulty.choices, default=Difficulty.BEGINNER
    )
    allow_reversed = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    blurb = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        ordering = ["sort_order", "card_count", "id"]

    def __str__(self):
        return f"{self.name} ({self.card_count} cards)"


class Reading(models.Model):
    session_key = models.CharField(max_length=255, blank=True, null=True)
    question = models.TextField()
    spread = models.ForeignKey(Spread, on_delete=models.SET_NULL, null=True, blank=True)
    spread_type = models.CharField(max_length=50)
    mode = models.CharField(max_length=20, default="ritual")  # ritual | daily | yesno
    created_at = models.DateTimeField(auto_now_add=True)
    ai_interpretation = models.TextField(blank=True, null=True)
    ai_summary = models.TextField(blank=True, default="")
    ai_advice = models.TextField(blank=True, default="")
    tone = models.CharField(max_length=40, blank=True, default="")
    verdict = models.CharField(max_length=20, blank=True, default="")

    def __str__(self):
        return f"{self.spread_type} - {self.created_at}"


class ReadingCard(models.Model):
    reading = models.ForeignKey(Reading, related_name="cards", on_delete=models.CASCADE)
    card = models.ForeignKey(TarotCard, on_delete=models.CASCADE)
    position_index = models.IntegerField()
    position_name = models.CharField(max_length=100)
    is_reversed = models.BooleanField(default=False)

    class Meta:
        ordering = ["position_index"]
