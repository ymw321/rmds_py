from typing import Dict, Union, List, Optional, Tuple
from logger_config import logger
from datetime import datetime, date
from abc import ABC, abstractmethod
from scipy.interpolate import interp1d
import csv
from curve import Curve, CurveManager, SimpleCurve

class Scenario:
    """Class representing a market scenario with BASE, UP, and DOWN perturbed curves."""
    def __init__(self, name: str, adate: date, base_curves: Dict[Tuple[str,date], Curve]):
        self.name = name
        self.date = adate
        self.base_curves = base_curves
        self.up_curves: Dict[Tuple[str, date], Curve] = {}
        self.down_curves: Dict[Tuple[str, date], Curve] = {}
        self._generate_perturbations()

    def _generate_perturbations(self):
        """Generates UP and DOWN perturbed curves."""
        for key, curve in self.base_curves.items():
            up_values = [v * 1.1 for v in curve.values]
            down_values = [v * 0.9 for v in curve.values]
            self.up_curves[key] = SimpleCurve(curve.name, curve.date, curve.dates, up_values)
            self.down_curves[key] = SimpleCurve(curve.name, curve.date, curve.dates, down_values)


class ScenarioManager:
    """Singleton class managing scenarios."""
    _instance = None
    scenarios: Dict[Tuple[str, date], Scenario] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScenarioManager, cls).__new__(cls)
        logger.info(f'ScenarioManager instance created!')
        return cls._instance

    def set_valuation_date(self, valuation_date: date):
        self.valuation_date = valuation_date

    def create_scenario(self, name: str, a_date: date):
        curve_manager = CurveManager()
        base_curves = curve_manager.curves
        scenario = Scenario(name, a_date, base_curves)
        self.scenarios[(name, a_date)] = scenario
        logger.info(f"Created scenario: {name} on {a_date}")

    def load_scenarios(self, scenario_file):
        # just the BASE for now
        # scenarios_data = pd.read_csv(scenario_file)
        logger.info(f"Start loading scenarios: first the BASE curves")
        self.create_scenario("BASE", self.valuation_date)

# Example usage:
if __name__ == "__main__":
    # Path to the curve file
    crv_file = "./tests/curves.csv"
    val_date = date(2020, 12, 30)
    
    # Initialize and run the CurveManager
    manager = CurveManager()
    manager.set_valuation_date(val_date)
    manager.load_curves(crv_file)

    scenMgr = ScenarioManager()
    scenMgr.set_valuation_date(val_date)
    scenMgr.load_scenarios(crv_file)    #note this version of scenMgr does not really load anything

    scenarios = scenMgr.scenarios
    for key, scen in scenarios.items():
        bases = scen.base_curves
        ups = scen.up_curves
        dns = scen.down_curves
        print(f'These are curves contained in scenario ' + key.__str__() + ':\n')
        print(bases.keys())
        for crv_key, crv in bases.items():
            print(crv_key)
            print(crv)
            print(crv.get_value(150))


