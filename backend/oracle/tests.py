from datetime import date
from unittest.mock import MagicMock, patch

from django.test import TestCase
from rest_framework.test import APIClient

from cards.meanings import CARD_MEANINGS, enrich_card, meaning_for
from cards.models import Arcana, Suit, TarotCard
from oracle.services import (
    build_prompt,
    parse_oracle_text,
    pick_daily_index,
    pick_daily_reversed,
    polarity_verdict,
)
from readings.models import Reading, Spread


class MeaningsTests(TestCase):
    def test_all_seventy_eight_cards_are_catalogued(self):
        self.assertEqual(len(CARD_MEANINGS), 78)

    def test_enrich_overrides_crypto_copy(self):
        payload = enrich_card(
            {
                "name": "The Fool",
                "keywords": [],
                "meanings_light": ["buy more coins"],
                "meanings_shadow": [],
            }
        )
        self.assertEqual(payload["name_cn"], "愚者")
        self.assertIn("开始", payload["keywords"])
        self.assertNotIn("buy more coins", payload["meanings_light"])

    def test_reversed_uses_shadow_meaning(self):
        light = meaning_for("The Sun", reversed=False)
        shadow = meaning_for("The Sun", reversed=True)
        self.assertNotEqual(light, shadow)
        self.assertIn("盲目", shadow)


class OracleServiceTests(TestCase):
    def test_parse_sectioned_response(self):
        text = """
---INTERPRETATION---
A path opens in the dark.
---SUMMARY---
先看清，再行动。
---ADVICE---
今晚只做一件事。
---TONE---
hopeful extra junk
---VERDICT---
lean_yes
"""
        parsed = parse_oracle_text(text, mode="yesno")
        self.assertEqual(parsed["interpretation"], "A path opens in the dark.")
        self.assertEqual(parsed["summary"], "先看清，再行动。")
        self.assertEqual(parsed["advice"], "今晚只做一件事。")
        self.assertEqual(parsed["tone"], "hopeful")
        self.assertEqual(parsed["verdict"], "lean_yes")

    def test_parse_rejects_unknown_tone_and_verdict(self):
        parsed = parse_oracle_text(
            "---INTERPRETATION---\nhi\n---TONE---\nchaotic\n---VERDICT---\nmaybe\n",
            mode="yesno",
        )
        self.assertEqual(parsed["tone"], "")
        self.assertEqual(parsed["verdict"], "unclear")

    def test_prompt_includes_reversal_and_spread(self):
        prompt = build_prompt(
            "我该离开吗",
            [
                {
                    "name": "The Tower",
                    "position": "Present",
                    "position_cn": "此刻",
                    "reversed": True,
                }
            ],
            spread_type="cross",
            spread_name_cn="十字牌阵",
            mode="ritual",
        )
        self.assertIn("逆位", prompt)
        self.assertIn("十字牌阵", prompt)
        self.assertIn("我该离开吗", prompt)

    def test_daily_index_is_deterministic(self):
        day = date(2026, 8, 12)
        self.assertEqual(pick_daily_index(day, 78), pick_daily_index(day, 78))
        self.assertNotEqual(pick_daily_index(day, 78), pick_daily_index(date(2026, 8, 13), 78))

    def test_polarity_verdict_respects_reversal(self):
        upright_sun = polarity_verdict([{"name": "The Sun", "reversed": False}])
        reversed_sun = polarity_verdict([{"name": "The Sun", "reversed": True}])
        self.assertEqual(upright_sun, "yes")
        self.assertIn(reversed_sun, {"lean_no", "no", "unclear"})


class TarotAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.fool = TarotCard.objects.create(
            name="The Fool",
            number=0,
            arcana=Arcana.MAJOR,
            suit=Suit.NONE,
            img="thefool.jpeg",
        )
        self.tower = TarotCard.objects.create(
            name="The Tower",
            number=16,
            arcana=Arcana.MAJOR,
            suit=Suit.NONE,
            img="thetower.jpeg",
        )
        self.spread, _ = Spread.objects.get_or_create(
            name="three_card",
            defaults={
                "name_cn": "三牌阵",
                "description": "past present future",
                "description_cn": "过去现在未来",
                "card_count": 3,
                "positions": ["The Past", "The Present", "The Future"],
                "positions_cn": ["过去", "现在", "未来"],
                "layout": [{"x": 22, "y": 50}, {"x": 50, "y": 50}, {"x": 78, "y": 50}],
                "category": "classic",
                "difficulty": "beginner",
            },
        )

    def test_cards_endpoint_returns_chinese_name(self):
        res = self.client.get("/api/tarot/cards/")
        self.assertEqual(res.status_code, 200)
        names = {row["name"]: row for row in res.json()}
        self.assertEqual(names["The Fool"]["name_cn"], "愚者")
        self.assertEqual(names["The Fool"]["element"], "Air")

    def test_spreads_endpoint_exposes_new_fields(self):
        res = self.client.get("/api/tarot/spreads/")
        self.assertEqual(res.status_code, 200)
        row = next(item for item in res.json() if item["name"] == "three_card")
        self.assertIn("三牌阵", row["name_cn"])
        self.assertEqual(row["positions_cn"][0], "过去")
        self.assertEqual(row["category"], "classic")

    def test_divine_requires_question_and_cards(self):
        res = self.client.post("/api/tarot/divine/", {"question": "hi"}, format="json")
        self.assertEqual(res.status_code, 400)

    @patch("oracle.views.consult_oracle")
    def test_divine_returns_structured_reading_and_persists(self, mock_consult):
        mock_consult.return_value = {
            "interpretation": "A tower falls so a road can appear.",
            "summary": "旧结构在塌，让路给真实。",
            "advice": "今晚只保留一件真正重要的事。",
            "tone": "transformative",
            "verdict": "",
        }
        res = self.client.post(
            "/api/tarot/divine/",
            {
                "question": "我该如何走下一步",
                "spread_type": "three_card",
                "mode": "ritual",
                "cards": [
                    {"name": "The Fool", "position": "The Past", "reversed": False},
                    {"name": "The Tower", "position": "The Present", "reversed": True},
                ],
            },
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIn("interpretation", body)
        self.assertEqual(body["summary"], "旧结构在塌，让路给真实。")
        self.assertEqual(body["advice"], "今晚只保留一件真正重要的事。")
        self.assertEqual(body["tone"], "transformative")
        self.assertTrue(body["reading_id"])
        reading = Reading.objects.get(id=body["reading_id"])
        self.assertEqual(reading.mode, "ritual")
        self.assertEqual(reading.cards.count(), 2)
        self.assertTrue(reading.cards.get(card=self.tower).is_reversed)

    @patch("oracle.views.consult_oracle")
    def test_yesno_fills_verdict_from_polarity_when_model_omits_it(self, mock_consult):
        mock_consult.return_value = {
            "interpretation": "The sun says walk.",
            "summary": "倾向是肯定的。",
            "advice": "去做。",
            "tone": "hopeful",
            "verdict": "",
        }
        res = self.client.post(
            "/api/tarot/divine/",
            {
                "question": "我该去吗",
                "spread_type": "yes_no",
                "mode": "yesno",
                "cards": [{"name": "The Fool", "reversed": False}],
            },
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["verdict"], "yes")

    def test_daily_is_stable_for_a_given_date(self):
        a = self.client.get("/api/tarot/daily/", {"date": "2026-08-12"})
        b = self.client.get("/api/tarot/daily/", {"date": "2026-08-12"})
        self.assertEqual(a.status_code, 200)
        self.assertEqual(a.json()["card"]["name"], b.json()["card"]["name"])
        self.assertEqual(a.json()["reversed"], b.json()["reversed"])
        self.assertIn("meaning", a.json())

    def test_daily_rejects_bad_date(self):
        res = self.client.get("/api/tarot/daily/", {"date": "08-12-2026"})
        self.assertEqual(res.status_code, 400)
