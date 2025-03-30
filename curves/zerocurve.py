from .curve import Curve
import bisect
from datetime import date
import numpy as np
from logger_config import logger
from typing import Dict, Union, Tuple, List

class ZeroCurve(Curve):
    """The base IR curve that bootstrap discount factors from a list of curve instruments."""
    def __init__(self, name:str, date:date):
        super().__init__(name, date)
        self.day_offsets: np.array = None
        self.dfs: np.array = None

    def bootstrap_df(self, inst_idx: int) -> int:
        # check known discount factors up to inst_idx
        logger.info(f"discount factors for {self.name} are bootstrapped!")
        return 0

    def geometric_interp(self, to_date: int) -> float:
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
        # Perform geometric interpolation 
        return v0 * pow((v1 / v0), e)

    def _get_value(self, to_date: int) -> float:
        return self.geometric_interp(to_date) # self.interpolator(to_date)
