class MockExtendedCalculations:
    def __init__(self):
        self.data = {
            "net_present_value": 10000,
            "internal_rate_of_return": 5.0,
            "lcoe": 0.1,
            "dynamic_payback_3_percent": 10,
            "total_roi_percent": 15,
            "co2_avoidance_per_year_tons": 2.5
        }

    def get_extended_calculations(self):
        return self.data

    def simulate_calculations(self):
        # Simulate some calculations for testing purposes
        return {
            "net_present_value": self.data["net_present_value"] * 1.1,
            "internal_rate_of_return": self.data["internal_rate_of_return"] + 1.0,
            "lcoe": self.data["lcoe"] * 0.9,
            "dynamic_payback_3_percent": self.data["dynamic_payback_3_percent"] - 1,
            "total_roi_percent": self.data["total_roi_percent"] + 5,
            "co2_avoidance_per_year_tons": self.data["co2_avoidance_per_year_tons"] + 0.5
        }