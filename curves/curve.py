from typing import Dict, Union, List, Optional, Tuple, Callable, NewType
import numpy as np
from logger_config import logger
from datetime import date, timedelta
from abc import ABC, abstractmethod
from scipy.interpolate import interp1d
from scipy.optimize import root_scalar
import csv
import bisect

Attributes = Dict[str, Union[str,float,int]]

# Abstract Class
class Curve:
    """Abstract base class for a curve."""
    # concrete method to initialize meta data for the curve
    def __init__(self, crv_name: str, crv_date:date):
        self.name = crv_name
        self.date = crv_date
        self.instruments: List[Curve._Instrument] = None
        self.day_offsets: np.array = None
        self.dfs: np.array = None

    def add_instrument(self, attributes: Dict[str, Union[str, int, float]]) -> None:
        instrument = Curve._Instrument(attributes)
        self.instruments.append(instrument)

    def sort_instruments(self):
        self.instruments.sort(key=lambda x: x.attributes['MaturityDate'])

    def generate(self, curves: Dict[Tuple[str, date], 'Curve'], inst_idx: int) -> int:
        # call different generate function depending on parameters given
        if curves and inst_idx: # with a complete market state and an idx of instrument, bootstrap from that instrument
            self.market_state = curves
            self.bootstrap_df(inst_idx)

    def bootstrap_df(self, inst_idx: int) -> int:  # to be implemented in ZeroCurve
        logger.info(f"only ZeroCurve has bootstrap_df() implemented!")
        return -1

    @abstractmethod
    def _get_value(self, a_date: int) -> float:
        pass

    def get_df(self, a_date) -> float:
        if isinstance(a_date, date):
            return self._get_value_by_date(a_date)
        elif isinstance(a_date, int):
            return self._get_value(a_date)
        else:
            raise TypeError("date must be a date object or an integer")

    # transform date to daycount based on Curve's daycount convention
    def _get_value_by_date(self, a_date: date) -> float:
        #assuming ACT/ACT for now. TODO: days will be calculated based on the daycount convention this curve has
        days = (a_date - self.date).days()
        return self._get_value(days)

    class _Instrument:
        """Class representing an interest rate instrument."""
        def __init__(self, attributes: Attributes):
            """
            Parameters:
                maturity (datetime): The maturity date of the instrument.
                market_value (float): The quoted market value of the instrument.
                pricing_function (Callable): A function to calculate the instrument's theoretical value given a curve.
            """
            #self.start_date = start_date # start_date is always the curve date
            self.maturity = attributes["MaturityDate"]
            self.market_value = attributes["MarketYield"]
            self.attributes = attributes

        def solve_for_df(self, curve: 'Curve', market_value: float, known_dfs: List[float]) -> float:
               def objective_function(df_n):
                   temp_curve = SimpleCurve(curve.dates.tolist(), known_dfs + [df_n])
                   market_state = {("temp_curve", self.attributes['maturity']): temp_curve}
                   return self.security.npv(market_state, self.attributes['maturity']) - market_value

               result = root_scalar(objective_function, bracket=[0.001, 1.0], method='bisect')
               if result.converged:
                   return result.root
               else:
                   raise ValueError(f"Failed to converge for instrument with maturity {self.attributes['maturity']}")

class SimpleCurve(Curve):
    """A simple curve with linear interpolation."""
    def __init__(self, name:str, date:date, day_offsets: int, dfs: float):
        super().__init__(name, date)
        self.day_offsets = np.array(day_offsets)
        self.dfs = np.array(dfs)

    def _get_value(self, to_date: int) -> float:
        # find the right point
        idx = bisect.bisect_left(self.day_offsets, to_date)

        # init the two bounding points for interpolation 
        t0, t1 = self.day_offsets[0], self.day_offsets[1] 
        v0, v1 = self.dfs[0], self.dfs[1] 
        #handle edge case: flat, or extrapolate
        if idx == 0:    #do not extrapolate leftward 
            return v0
        elif idx == len(self.day_offsets):    #extrapolate using the last two points
            t0, t1 = self.day_offsets[-2], self.day_offsets[-1] 
            v0, v1 = self.dfs[-2], self.dfs[-1] 

        # otherwise
        t0, t1 = self.day_offsets[idx - 1], self.day_offsets[idx] 
        v0, v1 = self.dfs[idx - 1], self.dfs[idx] 

        e = float((to_date - t0) / (t1 - t0))
        # Perform linear interpolation 
        return v0 + (v1 - v0) * e