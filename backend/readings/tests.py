from django.core.management import call_command
from django.test import TestCase

from readings.models import Spread


class PopulateSpreadsTests(TestCase):
    def test_populate_creates_twelve_named_spreads(self):
        call_command("populate_spreads")
        names = set(Spread.objects.values_list("name", flat=True))
        self.assertGreaterEqual(len(names), 12)
        self.assertIn("celtic_cross", names)
        self.assertIn("yes_no", names)
        self.assertIn("shadow", names)
        celtic = Spread.objects.get(name="celtic_cross")
        self.assertEqual(celtic.card_count, 10)
        self.assertEqual(len(celtic.positions_cn), 10)
        self.assertTrue(celtic.layout[1].get("overlay"))
