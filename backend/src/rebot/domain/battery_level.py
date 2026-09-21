from dataclasses import dataclass


@dataclass(frozen=True)
class BatteryLevel:
    percentage: int

    def __post_init__(self) -> None:
        if type(self.percentage) is not int:
            raise TypeError("Battery Level percentage must be an integer")
        if not 0 <= self.percentage <= 100:
            raise ValueError("Battery Level percentage must be between 0 and 100")

    def consume_one_percentage_point(self) -> BatteryLevel:
        if self.percentage == 0:
            raise RuntimeError("Battery Level cannot be consumed below zero")
        return BatteryLevel(self.percentage - 1)
