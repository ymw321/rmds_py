from typing import Dict, Union, Tuple, NewType, List
from datetime import date
from abc import ABC, abstractmethod

# forward reference
Curve = NewType('Curve', None)
CrvVector = Dict[Tuple[str,date],Curve]
#from curve import Curve

class Security(ABC):
    """Abstract class for a financial security."""
    def __init__(self, attributes: Dict[str, Union[str, float, int]]):
        self.security_id = attributes["SecId"]
        self.attributes = attributes
        self.type = "Security"
        self.val_date: date = None
        self.setup_security()

    @abstractmethod
    # each security must provide a list of curve names as market context 
    def require_curves(self) -> List[str]:
        pass

    @abstractmethod
    def setup_security(self):
        pass

    @abstractmethod
    def schedule_cashflows(self, val_date: date):
        self.val_date = val_date

    @abstractmethod
    def NPV(self, curves: CrvVector) -> float:
        pass

    @abstractmethod
    def __str__(self):
        pass
