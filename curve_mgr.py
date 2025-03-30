from typing import Dict, Union, List, Optional, Tuple, Callable, NewType
import numpy as np
from logger_config import logger
from datetime import date, timedelta
from abc import ABC, abstractmethod
from scipy.interpolate import interp1d
from scipy.optimize import root_scalar
import csv

import securities as sec

import curves as crv
Curve = crv.Curve
CrvVector = Dict[Tuple[str,date],Curve]
SimpleCurve = crv.SimpleCurve

# from curve import Curve
# from securities.security import Security
# from securities.bond import Bond, Equity
# from securities import sec_factory

Attributes = Dict[str, Union[str,float,int]]

# Abstract Singleton Curve Manager
# class CurveManager:
#     """Singleton class managing curves."""
class CurveManager:
    """Singleton class managing curves."""
    _instance = None
    curves: Dict[Tuple[str, date], Curve] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CurveManager, cls).__new__(cls)
            logger.info(f'CurveManager instance created!')
        return cls._instance

    def set_valuation_date(self, valuation_date: date):
        self.valuation_date = valuation_date

    # use read_curves_from_csv instead
    def load_curves(self, curve_file):
        self.read_curves_from_csv(curve_file)
        '''
        curves_data = pd.read_csv(curve_file)
        for _, row in curves_data.iterrows():
            dates = [date.strptime(d, "%Y-%m-%d") for d in row["dates"].split(";")]
            values = [float(v) for v in row["values"].split(";")]
            self.add_curve(SimpleCurve(name=row["curve_name"], date=self.valuation_date, dates=dates, values=values))
        '''
        
    def read_curves_from_csv(self, file_path):
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                curve_name = None
                curve_date = self.valuation_date
                curve_type = None
                dates = []
                values = []

                for row in reader:
                    if not row:  # Blank row indicates end of current curve
                        if curve_name and dates and values:
                            curve = SimpleCurve(name=curve_name, date=curve_date, day_offsets=dates, dfs=values)
                            self.add_curve(curve)
                            curve_name = None
                            dates = []
                            values = []
                    elif curve_name is None:  # Header row containing curve name
                        curve_name = row[0]
                        curve_date = date.fromisoformat(row[1])
                        curve_type = row[2]
                    else:  # Data rows containing <date, discount factor>
                        the_date = int(row[0])
                        the_value = float(row[1])
                        dates.append(the_date)
                        values.append(the_value)

                # Add the last curve if the file doesn't end with a blank row
                if curve_name and dates and values:
                    curve = SimpleCurve(name=curve_name, date=curve_date, day_offsets=dates, dfs=values)
                    self.add_curve(curve)
                    
            logger.info(f"Successfully read and added curves from CSV: {file_path}")

        except Exception as e:
            logger.error(f"Error reading curves from CSV file {file_path}: {e}")
            raise

    def add_curve(self, curve: Curve):
        key = (curve.name,curve.date)
        self.curves[key] = curve
        logger.info(f"Added curve: {curve.name}")

    def get_curve(self, name: str, to_date:date) -> Optional[Curve]:
        return self.curves.get((name,to_date))
    
# Example usage:
if __name__ == "__main__":
    # Path to the curve file
    config_file = "./tests/curves.csv"
    
    # Initialize and run the CurveManager
    manager = CurveManager()
    manager.set_valuation_date(date(2020, 12, 30))
    manager.load_curves(config_file)

    myCrv = manager.get_curve("OIS.USD", date(2020, 12, 30))
    print(myCrv.day_offsets)
    print(myCrv.get_df(150))
    crvKeys = list(manager.curves)
    print(crvKeys[0])
