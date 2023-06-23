from django.test import SimpleTestCase
from .custom_filters import calculate_start_index


class CalculateStartIndexTestCase(SimpleTestCase):
    def test_calculate_start_index(self):
        value = 30
        per_page = 10
        current_page = 2

        start_index = calculate_start_index(value, per_page, current_page)
        self.assertEqual(start_index, 11)

    def test_calculate_start_index_zero_value(self):
        value = 0
        per_page = 10
        current_page = 2

        start_index = calculate_start_index(value, per_page, current_page)
        self.assertEqual(start_index, 0)
