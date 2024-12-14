from typing import Dict, Union, List, Optional, Tuple
from logger_config import logger
from datetime import date
from abc import ABC, abstractmethod
from scipy.interpolate import interp1d
import csv
from curve import CurveManager, Curve
from scenario import ScenarioManager, Scenario
from security import SecurityManager, Security
import pandas as pd
import json as json

# Generic Calculation Function
def gen_rmds(sec_mgr: SecurityManager, scen_mgr: ScenarioManager) -> pd.DataFrame:
    data_store = []
    for (scenario_name, scenario_date), scenario in scen_mgr.scenarios.items():
        for security_id, security in sec_mgr.securities.items():
            try:
                val_date = scenario.date
                # cashflows are val_date dependent
                security.schedule_cashflows(val_date)
                base_npv = security.NPV(scenario.base_curves)
                up_npv = security.NPV(scenario.up_curves)
                down_npv = security.NPV(scenario.down_curves)
                data_store.append({
                    "Security ID": security_id,
                    "Scenario Name": scenario_name,
                    "Scenario Date": scenario_date,
                    "NPV_BASE": round(base_npv, 4),
                    "NPV_UP": round(up_npv, 4),
                    "NPV_DOWN": round(down_npv,4)
                })
                logger.info(f"Calculated NPVs for Security: {security_id}, Scenario: {scenario_name}")
            except Exception as e:
                logger.error(f"Error calculating NPV for Security: {security_id}, Scenario: {scenario_name}. Error: {e}")
    return pd.DataFrame(data_store)

# Task Dispatcher
from os import path
class TaskDispatcher:
    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.wk_folder = path.dirname(config_file)
        self.valuation_date = date.fromisoformat(self.config["valuation_date"])
        self.curve_manager = CurveManager()
        self.curve_manager.set_valuation_date(self.valuation_date)
        self.scen_mgr = ScenarioManager()
        self.scen_mgr.set_valuation_date(self.valuation_date)
        self.sec_mgr = SecurityManager()
        self.sec_mgr.set_valuation_date(self.valuation_date)

    def load_curves(self):
        curve_file = self.config["curve_definition_file"]
        self.curve_manager.load_curves(path.join(self.wk_folder, curve_file))

    def load_scenarios(self):
        scenario_file = self.config["scenario_definition_file"]
        self.scen_mgr.load_scenarios(path.join(self.wk_folder, scenario_file))

    def load_securities(self):
        security_file = self.config["security_definition_file"]
        self.sec_mgr.load_securities(path.join(self.wk_folder, security_file))

    def execute_use_case(self):
        use_case = self.config["use_case"]
        if use_case == "NPV_CALCULATION":
            results = gen_rmds(self.sec_mgr, self.scen_mgr)
            results.to_csv(path.join(self.wk_folder, self.config["output_file"]), index=False)
            logger.info(f"Results saved to {self.config['output_file']}")

    def run(self):
        try:
            logger.info("Starting Task Dispatcher...")
            self.load_curves()
            logger.info("Curves loaded")
            self.load_scenarios()
            logger.info("Scenarios loaded")
            self.load_securities()
            logger.info("Securities loaded")
            self.execute_use_case()
            logger.info("Task Dispatcher completed successfully.")
        except Exception as e:
            logger.error(f"Task Dispatcher encountered an error: {e}")

# Example Usage

if __name__ == "__main__":
    # Path to the configuration file
    config_file = "./tests/config.json"
    #config_file = "./rmds/tests/config.json"
    
    # Initialize and run the TaskDispatcher
    dispatcher = TaskDispatcher(config_file)
    dispatcher.run()
    