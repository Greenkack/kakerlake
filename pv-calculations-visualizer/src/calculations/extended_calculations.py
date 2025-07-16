class ExtendedCalculations:
    def __init__(self, total_investment, annual_savings, annual_production_kwh, pv_size_kwp):
        self.total_investment = total_investment
        self.annual_savings = annual_savings
        self.annual_production_kwh = annual_production_kwh
        self.pv_size_kwp = pv_size_kwp

    def calculate_npv(self, discount_rate, years):
        npv = 0
        for year in range(1, years + 1):
            npv += self.annual_savings / ((1 + discount_rate) ** year)
        npv -= self.total_investment
        return npv

    def calculate_irr(self, cash_flows):
        from numpy import irr
        return irr(cash_flows)

    def calculate_lcoe(self):
        return self.total_investment / self.annual_production_kwh

    def calculate_dynamic_payback(self, discount_rate):
        cumulative_cash_flow = -self.total_investment
        year = 0
        while cumulative_cash_flow < 0:
            year += 1
            cumulative_cash_flow += self.annual_savings / ((1 + discount_rate) ** year)
        return year

    def calculate_total_roi(self):
        return (self.annual_savings * 25 - self.total_investment) / self.total_investment * 100

    def calculate_co2_savings(self, co2_per_kwh):
        return self.annual_production_kwh * co2_per_kwh

    def display_results(self):
        results = {
            "NPV": self.calculate_npv(0.03, 25),
            "IRR": self.calculate_irr([-self.total_investment] + [self.annual_savings] * 25),
            "LCOE": self.calculate_lcoe(),
            "Dynamic Payback": self.calculate_dynamic_payback(0.03),
            "Total ROI": self.calculate_total_roi(),
        }
        return results