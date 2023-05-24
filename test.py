import unittest
from datetime import datetime
from calculator import calculate_cost

class TestCallCostCalculator(unittest.TestCase):
    def test_calculate_cost(self):
        parsed_data = [
            {
                "phone_number": "123456789",
                "start_time": datetime(2023, 5, 24, 8, 0, 0),
                "end_time": datetime(2023, 5, 24, 8, 5, 0),
            },
            {
                "phone_number": "987654321",
                "start_time": datetime(2023, 5, 24, 9, 0, 0),
                "end_time": datetime(2023, 5, 24, 9, 10, 0),
            },
            {
                "phone_number": "987654321",
                "start_time": datetime(2023, 5, 24, 9, 0, 0),
                "end_time": datetime(2023, 5, 24, 9, 10, 0),
            },
            {
                "phone_number": "623456769",
                "start_time": datetime(2023, 5, 24, 7, 0, 0),
                "end_time": datetime(2023, 5, 24, 7, 2, 0),
            },
        ]
        cost_struct = calculate_cost(parsed_data)
        self.assertEqual(cost_struct["123456789"], 5.0)
        self.assertEqual(cost_struct["987654321"], 0.0)
        self.assertEqual(cost_struct["623456769"], 1.0)

if __name__ == '__main__':
    unittest.main()
