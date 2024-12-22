from typing import Dict, Union, List, Optional, Tuple, NewType
from logger_config import logger
from datetime import date
from abc import ABC, abstractmethod
from scipy.interpolate import interp1d
import csv

import securities as sec
Security = sec.Security
#from securities.security import Security
#from securities.bond import Bond, Equity

from sec_factory import sec_factory

Attributes = Dict[str, Union[str,float,int]]

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

    def construct_and_add_security(self, attributes: Attributes) -> int:
        security_type = attributes.pop("SecType", None)
        security_id = attributes.get("SecId")

        try:
            security = sec_factory(security_type, attributes)
            self.add_security(security)
            logger.info(f"Constructed and added security of type {security_type}: {security_id}: {security}")
            return 0
        except Exception as e:
            logger.info(f"Failed instantiating Security {security_type}: {security_id}. Error returned from sec_factory: {e}")
            return -1

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
    scen_file = "./tests/scenarios.JSON"
    val_date = date(2020, 12, 30)
    
    # Initialize and run the CurveManager
    from curve import CurveManager
    manager = CurveManager()
    manager.set_valuation_date(val_date)
    manager.load_curves(crv_file)

    from scenario import ScenarioManager
    scenMgr = ScenarioManager()
    scenMgr.set_valuation_date(val_date)
    scenMgr.load_scenarios(scen_file)    #note this version of scenMgr does not really load anything

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
            print(sec.NPV(bases))
                