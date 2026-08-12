from rest_framework import serializers
from .models import TarotCard
from .meanings import enrich_card


class TarotCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TarotCard
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return enrich_card(data)
