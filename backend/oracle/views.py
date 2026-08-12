from datetime import date, datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cards.meanings import enrich_card, meaning_for
from cards.models import TarotCard
from cards.serializers import TarotCardSerializer
from readings.models import Reading, ReadingCard, Spread

from .services import (
    build_prompt,
    consult_oracle,
    pick_daily_index,
    pick_daily_reversed,
    polarity_verdict,
)


def _normalize_cards(raw_cards):
    normalized = []
    for item in raw_cards or []:
        if not isinstance(item, dict):
            continue
        name = (item.get("name") or "").strip()
        if not name:
            continue
        reversed_ = bool(item.get("reversed") or item.get("is_reversed"))
        normalized.append(
            {
                "name": name,
                "name_cn": item.get("name_cn") or "",
                "position": item.get("position") or "",
                "position_cn": item.get("position_cn") or "",
                "reversed": reversed_,
                "is_reversed": reversed_,
                "keywords": item.get("keywords") or [],
                "meaning": item.get("meaning") or meaning_for(name, reversed_),
            }
        )
    return normalized


def _persist_reading(question, spread, spread_type, mode, result, cards):
    reading = Reading.objects.create(
        question=question,
        spread=spread,
        spread_type=spread_type or (spread.name if spread else "reading"),
        mode=mode,
        ai_interpretation=result.get("interpretation") or "",
        ai_summary=result.get("summary") or "",
        ai_advice=result.get("advice") or "",
        tone=result.get("tone") or "",
        verdict=result.get("verdict") or "",
    )
    for index, item in enumerate(cards):
        db_card = TarotCard.objects.filter(name=item["name"]).first()
        if not db_card:
            continue
        ReadingCard.objects.create(
            reading=reading,
            card=db_card,
            position_index=index,
            position_name=item.get("position_cn") or item.get("position") or f"Position {index + 1}",
            is_reversed=bool(item.get("reversed")),
        )
    return reading


class DivinationView(APIView):
    def post(self, request):
        question = (request.data.get("question") or "").strip()
        cards_data = request.data.get("cards")
        spread_type = request.data.get("spread_type") or "reading"
        mode = (request.data.get("mode") or "ritual").strip().lower()
        if mode not in {"ritual", "daily", "yesno"}:
            mode = "ritual"

        if not question or not cards_data:
            return Response(
                {"error": "Missing question or cards"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cards = _normalize_cards(cards_data)
        if not cards:
            return Response(
                {"error": "No valid cards provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        spread = Spread.objects.filter(name=spread_type).first()
        spread_name_cn = ""
        if spread:
            spread_name_cn = spread.name_cn
            for i, card in enumerate(cards):
                if not card["position"] and i < len(spread.positions):
                    card["position"] = spread.positions[i]
                if not card["position_cn"] and i < len(spread.positions_cn or []):
                    card["position_cn"] = spread.positions_cn[i]

        prompt = build_prompt(
            question=question,
            cards=cards,
            spread_type=spread_type,
            spread_name_cn=spread_name_cn,
            mode=mode,
        )
        result = consult_oracle(prompt, mode=mode)

        if mode == "yesno" and not result.get("verdict"):
            result["verdict"] = polarity_verdict(cards)

        reading = _persist_reading(question, spread, spread_type, mode, result, cards)

        return Response(
            {
                "interpretation": result["interpretation"],
                "summary": result["summary"],
                "advice": result["advice"],
                "tone": result["tone"],
                "verdict": result.get("verdict") or "",
                "reading_id": reading.id,
            }
        )


class DailyOracleView(APIView):
    def get(self, request):
        raw_date = (request.query_params.get("date") or "").strip()
        if raw_date:
            try:
                day = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date, expected YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            day = date.today()

        qs = TarotCard.objects.all().order_by("arcana", "suit", "number", "id")
        n = qs.count()
        if n == 0:
            return Response(
                {"error": "No cards in the deck"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        index = pick_daily_index(day, n)
        card = qs[index]
        reversed_ = pick_daily_reversed(day)
        payload = enrich_card(TarotCardSerializer(card).data)
        meaning = meaning_for(card.name, reversed_)

        return Response(
            {
                "date": day.isoformat(),
                "card": payload,
                "reversed": reversed_,
                "meaning": meaning,
                "keywords": payload.get("keywords") or [],
            }
        )
