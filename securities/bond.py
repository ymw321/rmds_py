import sys
import os
# Get the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

from typing import Dict, Tuple, List
from logger_config import logger
from datetime import date

import curves as crv
Curve = crv.Curve
from .security import Security

class Bond(Security):
    """A simple bond implementation."""
    def __init__(self, attributes):
        super().__init__(attributes)
        self.type = "Bond"
        logger.info(Bond)

    def setup_security(self):
        pass

    def schedule_cashflows(self, val_date):
        super().schedule_cashflows(val_date)
        self.cashflow_dates = [1, 5, 7]
        self.cashflor_values = [100,120,100100]

    def require_curves(self) -> List[str]:
        return [self.attributes['DiscountCurve']]

    def NPV(self, curves: Dict[Tuple[str,date],Curve]) -> float:
        curve_name = self.attributes["DiscountCurve"]
        disc_curve = curves.get((curve_name, self.val_date))

        if not disc_curve:
            raise ValueError(f"Curve {curve_name} of date {self.val_date} not found in scenario.")

        npv = 0.0
        for i in range(0,2):
            discount_factor = disc_curve.get_df(self.cashflow_dates[i])
            npv += self.cashflor_values[i] * discount_factor
        return npv
    
    def __str__(self):
        return f"Bond Id={self.security_id} with maturity={self.attributes['MaturityDate']} and coupon={self.attributes['CouponRate']}"

class Equity(Security):
    def __init__(self, attributes):
        super().__init__(attributes)
        self.type = "Equity"
        logger.info(Equity)

    def setup_security(self):
        pass

    def require_curves(self) -> List[str]:
        return [self.attributes['EquityCurve']]

    def schedule_cashflows(self, val_date):
        super().schedule_cashflows(val_date)

    def NPV(self, curves: Dict[Tuple[str,date],Curve]) -> float:
        # Implement equity-specific NPV calculation
        npv = 0
        for curve_name, curve in curves.items():
            # Custom logic for NPV calculation for equities
            npv += sum(curve.dfs)  # Simplified example
        return npv
    
    def __str__(self):
        return f"Equity Id={self.security_id}"
