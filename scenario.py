from typing import Dict, Union, List, Optional, Tuple
from logger_config import logger
from datetime import date
from abc import ABC, abstractmethod
from scipy.interpolate import interp1d
import json as json
import csv
import curve as crv
Curve = crv.Curve
CurveManager = crv.CurveManager
ZeroCurve = crv.ZeroCurve
SimpleCurve = crv.SimpleCurve

class Scenario:
    """Class representing a market scenario with BASE, UP, and DOWN perturbed curves."""
    def __init__(self, name: str, a_date: date, base_curves: Dict[Tuple[str,date], Curve]):
        self.name = name
        self.date = a_date
        self.base_curves = base_curves
        self.up_curves: Dict[Tuple[str, date], Curve] = {}
        self.down_curves: Dict[Tuple[str, date], Curve] = {}
        self._generate_perturbations()

    def _generate_perturbations(self):
        """Generates UP and DOWN perturbed curves per senario.
        """
        for key, curve in self.base_curves.items():
            '''
            '''
            up_values = [v * 1.1 for v in curve.dfs]
            down_values = [v * 0.9 for v in curve.dfs]
            self.up_curves[key] = SimpleCurve(curve.name, curve.date, curve.day_offsets, up_values)
            self.down_curves[key] = SimpleCurve(curve.name, curve.date, curve.day_offsets, down_values)


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

    def define_perturb_matrx(self, ir_perturb_bps: float, ir_risk_factors: List):
        pass

    def define_scen_grid(self, ir_perturb_bps: float, ir_risk_factors: List):
        pass

    def load_scenarios(self, scenario_file):
        ''' read the scenario definition and create lists of shocks/perturbations
            1. given IR/CR/EQ perturbation amount and list of risk factors, create perturbation list
            2. based on shock and DV01 requirements, create scenario bases
            3. with each risk measure BASE, create a scanario that includes base, up, and down curves
        '''
        with open(scenario_file, 'r') as f:
            self.config = json.load(f)

        ir_perturb_bps = self.config.get("IR_perturb_bps", 10)
        ir_risk_factors = self.config.get("IR_risk_factors", [])
        self.define_perturb_matrx(ir_perturb_bps, ir_risk_factors)

        grid_def = self.config["scenario_grid"]


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


