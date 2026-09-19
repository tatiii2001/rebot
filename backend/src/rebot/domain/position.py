from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __post_init__(self) -> None:
        if type(self.x) is not int or type(self.y) is not int:
            raise TypeError("Position coordinates must be integers")
