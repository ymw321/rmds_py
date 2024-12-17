from typing import Dict, Tuple
from logger_config import logger
from datetime import date
import curve as crv
from curve import Curve
from .security import Security

class Bond(Security):
    """A simple bond implementation."""
    def __init__(self, security_id, attributes):
        super().__init__(security_id, attributes)
        logger.info(Bond)

    def setup_security(self):
        pass

    def schedule_cashflows(self, val_date):
        super().schedule_cashflows(val_date)
        self.cashflow_dates = [1, 5, 7]
        self.cashflor_values = [100,120,100100]

    def NPV(self, curves: Dict[Tuple[str,date],Curve]) -> float:
        curve_name = self.attributes["DiscountCurve"]
        disc_curve = curves.get((curve_name, self.val_date))

        if not disc_curve:
            raise ValueError(f"Curve {curve_name} of date {self.val_date} not found in scenario.")

        npv = 0.0
        for i in range(0,2):
            discount_factor = disc_curve.get_value(self.cashflow_dates[i])
            npv += self.cashflor_values[i] * discount_factor
        return npv
    
    def __str__(self):
        return f"Bond Id={self.attributes['SecId']} with maturity={self.attributes['Maturity']} and coupon={self.attributes['CpnRate']} instantiated"

class Equity(Security):
    def __init__(self, security_id, attributes):
        super().__init__(security_id, attributes)
        logger.info(Equity)

    def setup_security(self):
        pass

    def NPV(self, curves: Dict[Tuple[str,date],Curve]) -> float:
        # Implement equity-specific NPV calculation
        npv = 0
        for curve_name, curve in curves.items():
            # Custom logic for NPV calculation for equities
            npv += sum(curve.values)  # Simplified example
        return npv
    
    def __str__(self):
        return f"Equity Id={self.attributes['SecId']} instantiated"
