from typing import Dict, Union, List, Optional, Tuple
from logger_config import logger
from datetime import date
from abc import ABC, abstractmethod
from scipy.interpolate import interp1d
import csv
from curve import Curve, CurveManager, SimpleCurve
from scenario import Scenario, ScenarioManager

class Security(ABC):
    """Abstract class for a financial security."""
    def __init__(self, security_id: str, attributes: Dict[str, Union[str, float, int]]):
        self.security_id = security_id
        self.attributes = attributes
        self.val_date: date = None
        self.setup_security()

    @abstractmethod
    def setup_security(self):
        pass

    @abstractmethod
    def schedule_cashflows(self, val_date: date):
        self.val_date = val_date

    @abstractmethod
    def NPV(self, curves: Dict[Tuple[str,date],Curve]) -> float:
        pass


class Bond(Security):
    """A simple bond implementation."""
    def __init__(self, security_id, attributes):
        super().__init__(security_id, attributes)

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
            raise ValueError(f"Curve {curve_name} of date {val_date} not found in scenario.")

        npv = 0.0
        for i in range(0,2):
            discount_factor = disc_curve.get_value(self.cashflow_dates[i])
            npv += self.cashflor_values[i] * discount_factor
        return npv

class Equity(Security):
    def __init__(self, security_id, attributes):
        super().__init__(security_id, attributes)

    def setup_security(self):
        pass

    def NPV(self, scenario: Scenario) -> float:
        # Implement equity-specific NPV calculation
        npv = 0
        for curve_name, curve in scenario.base_curves.items():
            # Custom logic for NPV calculation for equities
            npv += sum(curve.values)  # Simplified example
        return npv

class SecurityManager:
    """Singleton class managing securities."""
    _instance = None
    securities: Dict[str, Security] = {}
    valuation_date: date = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecurityManager, cls).__new__(cls)
        return cls._instance

    def set_valuation_date(self, valuation_date: date):
        if valuation_date != self.valuation_date:
            self.valuation_date = valuation_date
            for id, sec in self.securities.items():
                sec.schedule_cashflows(valuation_date)
                logger.info(f'Security {id} cashflows are scheduled')

    def add_security(self, security: Security):
        self.securities[security.security_id] = security
        logger.info(f"Added security: {security.security_id}")

    def construct_and_add_security(self, attributes: dict) -> int:
        security_type = attributes.pop("SecType", None)
        security_id = attributes.get("SecId")

        if security_type == "Bond":
            security = Bond(security_id, attributes)
        elif security_type == "equity":
            security = Equity(security_id, attributes)
        else:
            logger.error(f"Unknown security type: {security_type}")
            return -1

        self.add_security(security)
        logger.info(f"Constructed and added security of type {security_type}: {security_id}")
        return 0

    def read_securities_from_tsv(self, file_path):
        cnt1 = int(0)
        cnt2 = int(0)
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file, delimiter='\t')
                for row in reader:
                    attributes = dict(row)
                    cnt2 += self.construct_and_add_security(attributes)
                    cnt1 += 1

            logger.info(f"Successfully read {cnt1} rows and added {cnt1+cnt2} securities from TSV: {file_path}")
        except Exception as e:
            logger.error(f"Error reading securities from TSV file {file_path}: {e}")
            raise

    def load_securities(self, security_file):
        self.read_securities_from_tsv(security_file)
        '''
        securities_data = pd.read_csv(security_file)
        for _, row in securities_data.iterrows():
            attributes = {
                "curve_name": row["curve_name"],
                "cash_flows": [
                    (datetime.strptime(d, "%Y-%m-%d"), float(a))
                    for d, a in zip(row["cash_flow_dates"].split(";"), row["cash_flow_amounts"].split(";"))
                ]
            }
            self.add_security(Bond(security_id=row["security_id"], attributes=attributes))
        '''

# Example usage:
if __name__ == "__main__":
    # Path to the curve file
    crv_file = "./tests/curves.csv"
    sec_file = "./tests/securities.tsv"
    val_date = date(2020, 12, 30)
    
    # Initialize and run the CurveManager
    manager = CurveManager()
    manager.set_valuation_date(val_date)
    manager.load_curves(crv_file)

    scenMgr = ScenarioManager()
    scenMgr.set_valuation_date(val_date)
    scenMgr.load_scenarios(crv_file)    #note this version of scenMgr does not really load anything

    secMgr = SecurityManager()
    secMgr.load_securities(sec_file)
    secMgr.set_valuation_date(val_date)

    secs = secMgr.securities
    scenarios = scenMgr.scenarios
    for id, sec in secs.items():
        print(id) 
        print(sec.attributes)
        for key, scen in scenarios.items():
            bases = scen.base_curves
            ups = scen.up_curves
            dns = scen.down_curves
            print(f'These are curves contained in scenario ' + key.__str__() + ':\n')
            print(bases.keys())
            print(sec.NPV(scen))
                