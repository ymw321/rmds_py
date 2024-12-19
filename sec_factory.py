from typing import Dict, Union, List, Optional, Tuple, NewType
import securities as sec
Security = sec.Security


def sec_factory(class_name, attributes) -> Security:
    classes = {
        "Bond": sec.Bond,
        "FloatBond": sec.Equity
    }
    
    if class_name in classes:
        return classes[class_name](attributes)
    else:
        raise ValueError(f"Unknown class name: {class_name}")

#example usage:
if __name__ == "__main__":
    bd_attributes = {"SecId": "bond1", "Maturity": "2029-12-18", "CpnRate": 0.05}
    eq_attributes = {"SecId": "eq1", "color": "Black"}

    dog = sec_factory("MyBond", bd_attributes)
    cat = sec_factory("MyEqty", eq_attributes)

    print(dog)  # Output: Bond Id=bond1 with maturity=2029-12-18 and coupon=0.05

    print(cat)  # Output: Equity Id=eq1

