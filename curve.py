from typing import Dict, Union, List, Optional, Tuple
import numpy as np
from logger_config import logger
from datetime import datetime, date, timedelta
from abc import ABC, abstractmethod
from scipy.interpolate import interp1d
import csv
import bisect

# Abstract Classes and Singleton Managers
class Curve:
    """Abstract base class for a curve."""
    # concrete method to initialize meta data for the curve
    def __init__(self, crv_name: str, crv_date:date):
        self.name = crv_name
        self.date = crv_date

    @abstractmethod
    def _get_value(self, date: int) -> float:
        pass

    def get_value(self, date) -> float:
        if isinstance(date, datetime):
            return self._get_value_by_date(date)
        elif isinstance(date, int):
            return self._get_value(date)
        else:
            raise TypeError("date must be a date object or an integer")

    # transform date to daycount based on Curve's daycount convention
    def _get_value_by_date(self, date: datetime) -> float:
        #assuming ACT/ACT for now
        days = (date - self.date).days()
        return self._get_value(days)

class SimpleCurve(Curve):
    """A simple curve with linear interpolation."""
    def __init__(self, name:str, date:date, dates: int, values: float):
        super().__init__(name, date)
        self.dates = np.array(dates)
        self.values = np.array(values)
        self.interpolator = interp1d(self.dates.astype(int), self.values, kind='linear', fill_value="extrapolate")

    def geometric_interp(self, to_date: int) -> float:
        # find the right point
        idx = bisect.bisect_left(self.dates, to_date)

        # init the two bounding points for interpolation 
        t0, t1 = self.dates[0], self.dates[1] 
        v0, v1 = self.values[0], self.values[1] 
        #handle edge case: flat, or extrapolate
        if idx == 0:    #do not extrapolate leftward 
            return v0
        elif idx == len(self.dates):    #extrapolate using the last two points
            t0, t1 = self.dates[-2], self.dates[-1] 
            v0, v1 = self.values[-2], self.values[-1] 

        # otherwise
        t0, t1 = self.dates[idx - 1], self.dates[idx] 
        v0, v1 = self.values[idx - 1], self.values[idx] 

        e = float((to_date - t0) / (t1 - t0))
        # Perform geometric interpolation 
        return v0 * pow((v1 / v0), e)

    def _get_value(self, to_date: int) -> float:
        return self.geometric_interp(to_date) # self.interpolator(to_date)

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
                            curve = SimpleCurve(curve_name, curve_date, dates, values)
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
                    curve = SimpleCurve(curve_name, curve_date, dates, values)
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
    config_file = "C:/dev/Python/rmds/tests/curves.csv"
    
    # Initialize and run the CurveManager
    manager = CurveManager()
    manager.set_valuation_date(date(2020, 12, 30))
    manager.load_curves(config_file)

    myCrv = manager.get_curve("OIS.USD", date(2020, 12, 30))
    print(myCrv.dates)
    print(myCrv.get_value(150))
    crvKeys = list(manager.curves)
    print(crvKeys[0])
